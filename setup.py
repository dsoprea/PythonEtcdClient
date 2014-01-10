#!/usr/bin/env python2.7

from setuptools import setup, find_packages
import sys, os

version = '2.0.1'

setup(name='etcd',
      version=version,
      description="A Python etcd client that just works.",
      long_description="""\
A Python etcd client that just works.""",
      classifiers=[
            'Intended Audience :: Developers',
            'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
            'Operating System :: POSIX :: Linux',
            'Programming Language :: Python :: 2.7',
            'Topic :: Database :: Front-Ends',
            'Topic :: Software Development :: Libraries :: Python Modules',
            'Topic :: System :: Distributed Computing',
      ], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='etcd',
      author='Dustin Oprea',
      author_email='myselfasunder@gmail.com',
      url='https://github.com/dsoprea/PythonEtcdClient',
      license='GPL 2',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
