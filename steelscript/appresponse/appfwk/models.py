# Copyright (c) 2019 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.

"""
This file defines custom models for this plugin

A custom model is a Django model - a Python class that is
backed by a database table.  This allows storage and retrieval
of custom data that is required by this plugin.

Many plugins do not require custom models and leave this file empty.

If models are defined, this plugin must be explicitly added
as an application in the local_settings.py file under LOCAL_APPS:

    LOCAL_APPS = (
        'steelscript.appresponse.appfwk',
    )

Often a related admin.py file is placed in this directory to provide
an interface for managing the model via the admin pages.

Sample model:

    class Product(models.Model):
        name = models.CharField(max_length=200)
        price = models.DecimalField(max_digits=7, decimal_places=3)
        count = models.IntegerField(default=1)

See https://docs.djangoproject.com/en/dev/ref/models/fields/ for a
full list of available models.

"""
