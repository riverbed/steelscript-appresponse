# Copyright (c) 2019 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.

"""
This file defines a custom admin page for any models defined
in models.py.

A sample admin page for the sample Product model in models.py:

    from django.contrib import admin

    from steelscript.appresponse.appfwk.models import Product

    class ProductAdmin(admin.ModelAdmin):
        list_display = ('name', 'price', 'count')

    admin.site.register(Product, ProductAdmin)

"""
