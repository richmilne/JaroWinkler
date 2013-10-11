#!/usr/bin/env python
# from distutils.core import setup
from setuptools import setup, find_packages

setup(
    name='jaro_winkler',
    version='1.0.2',
    description='Original, standard and customisable versions of the Jaro-Winkler functions.',
    author='Richard Milne',
    author_email='richmilne@hotmail.com',
    url='https://github.com/richmilne/JaroWinkler.git',
    packages=['jaro'],
    include_package_data=True,
    platforms=['any'],
    license='GNU General Public License v3 (GPLv3)',
    classifiers=[
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 2',
        'Topic :: Text Processing',
        'Topic :: Text Processing :: General',
        'Topic :: Text Processing :: Indexing',
    ],
     )

