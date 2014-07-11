#!/usr/bin/env python2.7

import setuptools
import sys
import os.path

import etcd

app_path = os.path.dirname(etcd.__file__)

long_description = "A Python etcd client that just works."

with open(os.path.join(app_path, 'resources', 'requirements.txt')) as f:
      install_requires = list(map(lambda s: s.strip(), f.readlines()))

setuptools.setup(
      name='etcd',
      version=etcd.__version__,
      description="A Python etcd client that just works.",
      long_description=long_description,
      classifiers=[
            'Intended Audience :: Developers',
            'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
            'Operating System :: POSIX :: Linux',
            'Topic :: Database :: Front-Ends',
            'Topic :: Software Development :: Libraries :: Python Modules',
            'Topic :: System :: Distributed Computing',
      ],
      keywords='etcd kv',
      author='Dustin Oprea',
      author_email='myselfasunder@gmail.com',
      url='https://github.com/dsoprea/PythonEtcdClient',
      license='GPL 2',
      packages=setuptools.find_packages(exclude=[]),
      include_package_data=True,
      zip_safe=False,
      install_requires=install_requires,
)
