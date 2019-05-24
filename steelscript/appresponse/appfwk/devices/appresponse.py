# Copyright (c) 2019 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.


from steelscript.appresponse.core.appresponse import AppResponse


def new_device_instance(*args, **kwargs):
    ar = AppResponse(*args, **kwargs)
    return ar
