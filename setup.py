#!/usr/bin/env python
import os
from setuptools import setup, find_packages

with open('requirements.txt') as f:
    install_requires = f.read().splitlines()

postgres_requires = [
    'psycopg2>=2.5.0,<2.6.0',
]

mysql_requires = [
    'MySQL-python>=1.2.0,<1.3.0',
]

setup(
    name='tlog',
    version='0.2.5',
    author='Thomas Erlang',
    author_email='thomas@erlang.dk',
    url='https://github.com/thomaserlang/tlog',
    description='Multi logging platform, powerful filters, real-time notifications and early warning system.',
    long_description=__doc__,
    package_dir={'': 'src'},
    packages=find_packages('src'),
    zip_safe=False,
    install_requires=install_requires,
    extras_require={
        'postgres': install_requires + postgres_requires,
        'mysql': install_requires + mysql_requires,
    },
    license=None,
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'tlog = tlog.runner:main',
        ],
    },
    classifiers=[],
)