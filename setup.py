# Copyright (c) 2019 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.

from glob import glob

from setuptools import setup, find_packages
from gitpy_versioning import get_version

install_requires = (
    'steelscript>=2.0',
    'sleepwalker>=2.0',
    'reschema>=2.0'
)

setup_args = {
    'name':                'steelscript.appresponse',
    'namespace_packages':  ['steelscript'],
    'version':             get_version(),
    'author':              'Riverbed Technology',
    'author_email':        'eng-github@riverbed.com',
    'url':                 'http://pythonhosted.org/steelscript',
    'license':             'MIT',
    'description':         'Python modules to interact AppResponse via its REST API',
    'long_description':    """SteelScript for AppResponse
===========================

Python modules to interact AppResponse via REST API.

For a complete guide to installation, see:

http://pythonhosted.org/steelscript/
    """,

    'platforms': 'Linux, Mac OS, Windows',

    'classifiers': [
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.5',
        'Topic :: System :: Networking',
    ],

    'python_requires': '>3.5.0',

    'packages': find_packages(exclude=('gitpy_versioning',)),

    'data_files': (
        ('share/doc/steelscript/docs/appresponse', glob('docs/*')),
        ('share/doc/steelscript/examples/appresponse', glob('examples/*')),
    ),

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

}

setup(**setup_args)
