#!/usr/bin/env python
import pathlib
from setuptools import setup, find_packages

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / 'README.md').read_text()

# TODO: Package / expose functionality on the command line, too.

setup(
    name='jaro_winkler',
    version='2.0.0',
    description='Original, standard and customisable versions of the Jaro-Winkler functions.',
    long_description=README,
    long_description_content_type='text/markdown',
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
        'Programming Language :: Python :: 3',
        'Topic :: Text Processing',
        'Topic :: Text Processing :: General',
        'Topic :: Text Processing :: Indexing',
    ],
)