#!/usr/bin/env python

import os
import sys
from codecs import open

from setuptools import setup


if sys.argv[-1] == 'publish':
    os.system('python setup.py register')
    os.system('python setup.py sdist upload')
    os.system('python setup.py bdist_wheel upload --universal')
    sys.exit()


requires = [
    r.strip() for r in open('requirements.txt').readlines() if not r.strip().startswith('#') and r.strip()
]


version = '1.0.0'


setup(
    name='watch',
    version=version,
    description='Watch things on your Apple TV',
    long_description=open('README.md').read(),
    author='Brenton Cleeland',
    author_email='brenton@brntn.me',
    url='https://github.com/sesh/watch',
    packages=['watch'],
    package_data={
        '': ['LICENSE', 'README.md', 'requirements.txt']
    },
    include_package_data=True,
    entry_points={
        'console_scripts': ['watch=watch.watch:main'],
    },
    install_requires=requires,
    license='MIT',
    classifiers=(
        'Environment :: Console',
        'License :: OSI Approved :: MIT License (MIT)',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
    )
)
