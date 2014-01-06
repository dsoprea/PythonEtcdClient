#!/usr/bin/env python2.7

from setuptools import setup, find_packages
import sys, os

version = '1.1.2'

setup(name='etcd',
      version=version,
      description="A Python etcd client that just works.",
      long_description="""\
A Python etcd client that just works.""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
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
