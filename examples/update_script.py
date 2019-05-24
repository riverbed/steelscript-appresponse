#!/usr/bin/env python

# Copyright (c) 2019 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.

import optparse
import os
import json

from time import sleep
from urllib.parse import urlparse
from steelscript.appresponse.core.app import AppResponseApp
from steelscript.common.exceptions import RvbdHTTPException


class UpdateApp(AppResponseApp):

    def add_options(self, parser):
        super(UpdateApp, self).add_options(parser)

        group = optparse.OptionGroup(parser, "Image URL options")
        group.add_option('--image_path', dest='image_path',
                         default=None,
                         help='Path to local update image')
        group.add_option('--image_url', dest='image_url',
                         default=None, help='Image URL')
        parser.add_option_group(group)

    def validate_args(self):
        try:
            super(UpdateApp, self).validate_args()
            if (self.options.image_url is not None and
                    self.options.image_path is not None):
                self.parser.error("Either --image_path or --image_url "
                                  "has to be provided but not both")
            elif self.options.image_url is not None:
                result = urlparse(self.options.image_url)
                if not (result.scheme and result.netloc and result.path):
                    self.parser.error("Please, provide valid --image_url")
            elif self.options.image_path is not None:
                if not (os.path.exists(self.options.image_path)):
                    self.parser.error("Please, provide valid --image_path")
            elif (self.options.image_url is None and
                  self.options.image_path is None):
                self.parser.error("Please, provide either"
                                  " --image_path or --image_url")
        except RvbdHTTPException as e:
            self.parser.error("Failed to validate options: {}"
                              .format(e.error_text))

    def upload_image(self, path):
        try:
            print("Image path: {}".format(path))
            resp = (self.appresponse
                        .system_update
                        .upload_image(path))
            if resp is not None:
                print("Upload successfully started ...")
                id_ = json.loads(resp)['id']
                uploaded = False
                while not uploaded:
                    progress = int((self.appresponse
                                        .system_update
                                        .get_image_by_id(id_)
                                        .progress()))
                    print("Upload progress: {}%".format(progress))
                    if progress == 100:
                        uploaded = True
                    else:
                        sleep(15)
                if uploaded:
                    return id_
                else:
                    return False
            else:
                raise ValueError('Failed to upload an update image')
        except RvbdHTTPException as e:
            if str(e).startswith('404'):
                raise ValueError('Failed to upload an update image')

    def fetch_image(self, url):
        try:
            print("Image URL: {}".format(url))
            image = self.appresponse.system_update.fetch_image(url)
            if image is not None:
                print("Fetch successfully started ...")
                id_ = image.id()
                fetched = False
                while not fetched:
                    progress = int((self.appresponse
                                        .system_update
                                        .get_image_by_id(id_)
                                        .progress()))
                    print("Fetching progress: {}%".format(progress))
                    if progress == 100:
                        fetched = True
                    else:
                        sleep(15)
                if fetched:
                    return id_
                else:
                    return False
            else:
                raise ValueError('Failed to fetch an update image')
        except RvbdHTTPException as e:
            if str(e).startswith('404'):
                raise ValueError('Failed to fetch an update image')

    def initialize_update(self):
        try:
            update = self.appresponse.system_update.get_update()
            if update is not None:
                if update.state() != 'IDLE':
                    print("Resetting into IDLE state ...")
                    update.reset()
                    reset = False
                    while not reset:
                        if (self.appresponse
                                .system_update
                                .get_update()
                                .state()) == 'IDLE':
                            reset = True
                        else:
                            sleep(15)
                update.initialize()
                if (self.appresponse
                        .system_update
                        .get_update()
                        .state()) != 'INITIALIZED':
                    print("Initializing ...")
                    initialized = False
                    while not initialized:
                        state = (self.appresponse
                                     .system_update
                                     .get_update()
                                     .state())
                        if state == 'INITIALIZED':
                            initialized = True
                        elif state == 'INITIALIZING':
                            sleep(15)
                        else:
                            return False
                    if initialized:
                        return True
                else:
                    return True
        except RvbdHTTPException as e:
            if str(e).startswith('404'):
                raise ValueError('Failed to initialize an update')

    def start_update(self):
        try:
            self.appresponse.system_update.get_update().start()
            print("Update started ...")
        except RvbdHTTPException as e:
            if str(e).startswith('404'):
                raise ValueError('Failed to start an update process')

    def is_valid_image(self, id_):
        try:
            print("Validating the image ...")
            validated = False
            while not validated:
                state = (self.appresponse
                             .system_update
                             .get_image_by_id(id_)
                             .state())
                if state != 'VALIDATING':
                    validated = True
                else:
                    sleep(15)
            if (self.appresponse
                    .system_update
                    .get_image_by_id(id_)
                    .state()) == 'VALID':
                return True
            else:
                return False
        except RvbdHTTPException as e:
            if str(e).startswith('404'):
                raise ValueError('Failed to validate an image')

    def main(self):
        try:
            if self.options.image_url is not None:
                id_ = self.fetch_image(self.options.image_url)
                if isinstance(id_, int):
                    if self.is_valid_image(id_):
                        if self.initialize_update():
                            self.start_update()
                        else:
                            self.parser.error('Failed to initialize')
                    else:
                        self.parser.error('Invalid update image')
                else:
                    self.parser.error('Failed to fetch an update image')
            elif self.options.image_path is not None:
                id_ = self.upload_image(self.options.image_path)
                if isinstance(id_, int):
                    if self.is_valid_image(id_):
                        if self.initialize_update():
                            self.start_update()
                        else:
                            self.parser.error('Failed to initialize')
                    else:
                        self.parser.error('Invalid update image')
                else:
                    self.parser.error('Failed to upload an update image')
            else:
                self.parser.error('Neither path or url provided')
        except RvbdHTTPException as e:
            if str(e).startswith('404'):
                raise ValueError('Failed to fetch or upload an update image')


if __name__ == '__main__':
    app = UpdateApp()
    app.run()
