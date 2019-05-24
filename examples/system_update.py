#!/usr/bin/env python

# Copyright (c) 2019 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.

"""
Demonstrate System Update API.
"""

from time import sleep
from urllib.parse import urlparse
from steelscript.appresponse.core.app import AppResponseApp
from steelscript.common.exceptions import RvbdHTTPException
from steelscript.commands.steel import prompt_yn


class SystemUpdateApp(AppResponseApp):

    def main(self):
        print("-----------------------------")
        print("Demonstrate System Update API")
        print("-----------------------------")

        try:
            print("")
            print("---Update images---")
            images = self.appresponse.system_update.get_images()
            if images:
                print("Images count: " + str(len(images)))
            else:
                print("No images available")
        except RvbdHTTPException as e:
            if str(e).startswith('404'):
                raise ValueError('Failed to get an update images')

        try:
            print("")
            print("---Fetch image---")
            url = input('Please, enter an update image url: ').strip()
            try:
                result = urlparse(url)
                if result.scheme and result.netloc and result.path:
                    image = self.appresponse.system_update.fetch_image(url)
                    if image is not None:
                        print("Fetch successfully started")
                        print("Wait 5 sec ...")
                        sleep(5)
                else:
                    print('Invalid update image url')
            except RvbdHTTPException as e:
                if str(e).startswith('404'):
                    raise ValueError('Invalid update image url')
        except RvbdHTTPException as e:
            if str(e).startswith('404'):
                raise ValueError('Failed to fetch an update image')

        try:
            print("")
            print("---Update Image Details---")
            images = self.appresponse.system_update.get_images()
            if len(images) > 0:
                try:
                    id_ = images[-1].id()
                    image = (self.appresponse
                                 .system_update
                                 .get_image_by_id(id_))
                    if image is not None:
                        image.print_properties()
                    else:
                        print("No image retrieved")
                except RvbdHTTPException as e:
                    if str(e).startswith('404'):
                        raise ValueError('Failed to get image')

                try:
                    id_ = images[-1].id()
                    image = (self.appresponse
                                 .system_update
                                 .get_image_by_id(id_))
                    if image is not None:
                        print("")
                        print("---Delete Image---")
                        image.delete()
                        print("Image deleted")
                except RvbdHTTPException as e:
                    if str(e).startswith('404'):
                        raise ValueError('Failed to delete image')
            else:
                print("No images available")
        except RvbdHTTPException as e:
            if str(e).startswith('404'):
                raise ValueError('Failed to get an update images')

        try:
            print("")
            print("---Update Details---")
            update = self.appresponse.system_update.get_update()
            if update is not None:
                update.print_properties()
                print("")
                print("--Initialize an update if in"
                      " IDLE state or reset it--")
                print("Update state: " + update.state())
                if update.state() == 'IDLE':
                    print("Initializing and resetting")
                    update.initialize()
                    print("Wait 10 sec ...")
                    sleep(10)
                    print("Resetting into IDLE state")
                    update.reset()
                else:
                    print("Resetting into IDLE state")
                    update.reset()
                print("")
                print("---How to execute an update---")
                print("In order to execute an update run those steps:")
                print("1. Initialize update: update.initialize()")
                print("2. Run update: update.start()")
                print("Those steps will bring box down and it will be"
                      " inaccessible for some time")
            else:
                print("No update retrieved")
        except RvbdHTTPException as e:
            if str(e).startswith('404'):
                raise ValueError('Failed to get an update')


if __name__ == '__main__':
    if prompt_yn('\nSystem update demonstration might be time consuming.'
                 ' Would you like to continue?',
                 default_yes=False):
        app = SystemUpdateApp()
        app.run()
