#!/usr/bin/env python

# Copyright (c) 2019 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.

"""
Demonstrate SSL Certificate API
"""

from steelscript.appresponse.core.app import AppResponseApp
from steelscript.common.exceptions import RvbdHTTPException


class CertificateApp(AppResponseApp):

    def main(self):
        print("-------------------------------")
        print("Demonstrate SSL Certificate API")
        print("-------------------------------")
        try:
            print("Certificate Details")
            print("-------------------")
            certificate = self.appresponse.certificate.get_certificate()
            if certificate is not None:
                certificate.print_properties()
            else:
                print("No certificate retrieved")
        except RvbdHTTPException as e:
            if str(e).startswith('404'):
                raise ValueError('Failed to get Certificate.')


if __name__ == '__main__':
    app = CertificateApp()
    app.run()
