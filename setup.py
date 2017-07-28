# Copyright (c) 2017 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.

"""
steelscript.appresponse
====================
Python modules to interact AppResponse via REST API

"""
from setuptools import setup, find_packages
from gitpy_versioning import get_version

install_requires = (
    'steelscript',
    'sleepwalker',
    # Add any special python package requirements below this line
)

setup_args = {
    'name':                'steelscript.appresponse',
    'namespace_packages':  ['steelscript'],
    'version':             get_version(),

    # Update the following as needed
    'author':              'Riverbed',
    'author_email':        'eng-github@riverbed.com',
    'url':                 '',
    'license':             'MIT',
    'description':         'Python modules to interact AppResponse via REST API',
    'long_description':    __doc__,

    'packages': find_packages(exclude=('gitpy_versioning',)),
    'zip_safe': False,
    'install_requires': install_requires,
    'extras_require': None,
    'test_suite': '',
    'include_package_data': True,
    'entry_points': {
        'steel.commands': [
            'appresponse = steelscript.appresponse.commands'
        ],
        'portal.plugins': [
            'appresponse = steelscript.appresponse.appfwk.plugin:AppResponsePlugin'
        ],
    },

    'classifiers': (
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Operating System :: OS Independent',
        'Topic :: Software Development'
    ),
}

setup(**setup_args)
