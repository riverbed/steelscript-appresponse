# Copyright (c) 2015 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.

"""
This file defines a device associated with this plugin
"""

#
# new_device_instance
#
# Implement this method to return a device instance to the target
# host/port using the request authentication credentials.
#
# This function must return an object that can be used to
# interact with this device.  The object returned can be of
# any type, and the methods used to interact with the actual
# device are implementation specific.
#
# This method is called as a consequence of:
#    dev = DeviceManager.get_device(id)
#
# The above is normally invoked from a datasource TableQuery.run()
# method just before interacting with the device to perform
# a query.
#
# The device associated with id is looked up in the Device database
# table and the new_device_instance() method is invoked for that
# device's module.
#
# The returned object is cached by the device id and returned
# on subsequent calls to get_device() for the same id.  The object
# is then returned to the caller.
#
# This method should *only* be used if the resulting device object
# is thread-safe and can handle interactions from multiple jobs
# simultaneously.
#

def new_device_instance(host, port, auth):
    # This function must be implemented and should return
    # a device object.
    return None
