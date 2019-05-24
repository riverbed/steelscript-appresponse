#!/usr/bin/env python

# Copyright (c) 2019 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.

"""
Demonstrate SSL Keys API.
"""
import os
import subprocess
import random
from steelscript.appresponse.core.app import AppResponseApp
from steelscript.common.exceptions import RvbdHTTPException


class SslKeysApp(AppResponseApp):

    def main(self):
        print("------------------------")
        print("Demonstrate SSL Keys API")
        print("------------------------")

        try:
            print("")
            print("---Import SSL Key---")
            filename = '/tmp/key.pem'
            cmd = 'openssl genrsa -out ' + filename + ' 2048'
            p = subprocess.Popen(cmd, shell=True,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.STDOUT)
            p.wait()
            random_n = str(random.randint(1, 10))
            data = dict(name='Demo_Key_' + random_n,
                        key=open(filename).read(),
                        passphrase='DemoPassphrase_' + random_n,
                        description='Demo_Description_' + random_n)
            try:
                os.remove(filename)
            except OSError:
                pass
            key = self.appresponse.ssl_key_store.import_key(data)
            if key is not None:
                print("Key successfully imported")
                print(key)
        except RvbdHTTPException as e:
            if str(e).startswith('404'):
                raise ValueError('Failed to import SSL Key')

        try:
            print("")
            print("---SSL Keys Count---")
            keys = self.appresponse.ssl_key_store.get_keys()
            if keys:
                print(str(len(keys)))
            else:
                print('0')
        except RvbdHTTPException as e:
            if str(e).startswith('404'):
                raise ValueError('Failed to get SSL Keys.')

        try:
            print("")
            print("---SSL Key Details---")
            id_ = keys[-1].id()
            key = (self.appresponse
                       .ssl_key_store
                       .get_key_by_id(id_))
            if key is not None:
                key.print_properties()
            else:
                print("No SSL Key retrieved")
        except RvbdHTTPException as e:
            if str(e).startswith('404'):
                raise ValueError('Failed to get SSL Key')

        try:
            print("")
            print("---Delete SSL Key---")
            id_ = keys[-1].id()
            key = (self.appresponse
                       .ssl_key_store
                       .get_key_by_id(id_))
            if key is not None:
                key.datarep.execute('delete')
                print("Key deleted.")
        except RvbdHTTPException as e:
            if str(e).startswith('404'):
                raise ValueError('Failed to delete SSL Key')

        try:
            print("")
            print("---SSL Keys Count---")
            keys = self.appresponse.ssl_key_store.get_keys()
            if keys:
                print(str(len(keys)))
            else:
                print('0')
        except RvbdHTTPException as e:
            if str(e).startswith('404'):
                raise ValueError('Failed to get SSL Keys')


if __name__ == '__main__':
    app = SslKeysApp()
    app.run()
