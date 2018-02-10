#!/usr/bin/env python
# -*- encoding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function

import io
import re
from glob import glob
from os.path import basename
from os.path import splitext

from setuptools import find_packages
from setuptools import setup


setup(
    name='gpopup',
    version='0.1.0',
    license='BSD',
    description='Popup menu using GTK3',
    long_description='Popup menu using GTK3',
    author='Idaho Frost',
    author_email='frostidaho@gmail.com',
    url='https://github.com/frostidaho/python-gpopup',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    py_modules=[splitext(basename(path))[0] for path in glob('src/*.py')],
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        # complete classifier list: http://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: Unix',
        'Operating System :: POSIX',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Utilities',
    ],
    keywords=[],
    install_requires=[
        'pygobject',
    ],
    extras_require={},
    entry_points={
        'console_scripts': [
            'gpopup-send = gpopup.cli_send:main',
            'gpopup-client = gpopup.cli_client:main',
            'gpopup-server = gpopup.cli_server:main',
        ]
    },
)
