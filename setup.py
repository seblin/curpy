#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (C) 2019  Sebastian Linke

# This file is part of Curpy.

# Curpy is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Curpy is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Curpy.  If not, see <https://www.gnu.org/licenses/>.

import os
import setuptools
import sys

import curpy

# fromisoformat() (datetime module) was introduced in Python 3.7
if sys.version_info < (3, 7):
    sys.exit('ERROR: Python interpreter version must be 3.7 or higher')

WINDOWS = os.name == 'nt'

def main():
    setuptools.setup(
        name='curpy',
        version=curpy.__version__,
        description='A tool for converting between currencies',
        long_description=open('README.rst').read(),
        author='Sebastian Linke',
        author_email='Seb_Linke@arcor.de',
        url='https://github.com/seblin/curpy',
        license='GPL v3',
        platforms = 'any',
        classifiers=[
            'Environment :: Console',
            'Intended Audience :: Developers',
            'Intended Audience :: End Users/Desktop',
            'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
            'Natural Language :: English',
            'Operating System :: OS Independent',
            'Programming Language :: Python :: 3.7',
            'Topic :: System :: Shells',
        ],
        packages=['curpy'],
        scripts=['bin/curpy' + '.bat' if WINDOWS else '']
    )

if __name__ == '__main__':
    main()
