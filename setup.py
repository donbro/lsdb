#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#         lsdb is a meta-data multi-tool
#
#	filesystem meta-data --> database (postgres)
#
#  Copyright (C) 2020 Terrestrial Downlink LLC <https://www.terrestrialdownlink.org>
#
#

# read the contents of your README file
from os import path

from setuptools import setup,find_packages

##

this_directory = path.abspath(path.dirname(__file__)) # '/Users/donb/py_dev/lsdb'

with open(path.join(this_directory, 'README.rst')) as f:
    long_description = f.read()

##

setup(
    name='lsdb',
    version='0.1.3',
    description="A multi-tool for your metadata",
    long_description=long_description,
    #long_description_content_type='text/markdown',
    author='Don Brotemarkle',
    author_email='donbro@mac.com',
    url='https://github.com/donbro/lsdb',
    packages=find_packages(),
    package_data={'': ['../LICENSE', '../README.rst']},
    include_package_data=True,
    install_requires=[
        'Click',
    ],

    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=2.7'
)

# [https://packaging.python.org/guides/making-a-pypi-friendly-readme/]
