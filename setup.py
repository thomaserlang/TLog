#!/usr/bin/env python
import os
from setuptools import setup, find_packages

with open('requirements.txt') as f:
    install_requires = f.read().splitlines()

setup(
    name='tlog',
    version='0.0.1',
    author='Thomas Erlang',
    author_email='thomas@erlang.dk',
    url='http://tesoft.dk/tlog',
    description='TLog',
    long_description=__doc__,
    package_dir={'': 'src'},
    packages=find_packages('src'),
    zip_safe=False,
    install_requires=install_requires,
    license=None,
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'tlog = tlog.runner:main',
        ],
    },
    classifiers=[],
)