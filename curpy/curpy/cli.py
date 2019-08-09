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

from argparse import ArgumentParser, RawTextHelpFormatter
from sys import stdin
from textwrap import dedent

from . import __version__
from .api import convert_string, get_currency_codes

def get_argument_parser(version=__version__):
    parser = ArgumentParser(
        prog='curpy', formatter_class=RawTextHelpFormatter,
        usage='curpy [-h] [-v] [-l]\n'
              # Space for "usage: curpy "
              '             [conversion [conversion ...]]\n'
              '             [conversion options]',
        description='Converts foreign currencies.'
    )
    parser.add_argument(
        '-v', '--version', action='version', version=f'%(prog)s {version}'
    )
    parser.add_argument(
        '-l', '--list-codes', action='store_true',
        help='show available currency codes and exit'
    )
    parser.add_argument('conversions', nargs='*',
                        help=dedent("""\
                        Defines the desired conversion expecting this format:
                        "amount currency_code_origin in currency_code_target"

                        (Example: "42.23 EUR in USD")

                        This argument can be used multiple times. If omitted
                        then the strings are read from standard input (STDIN).
                        Each conversion result is shown in a new line.""")
    )
    convgroup = parser.add_argument_group('conversion options')
    convgroup.add_argument(
        '-p', '--precision', metavar='N', type=int, default=2,
        help='the result\'s precision (number of decimal places)'
    )
    convgroup.add_argument(
        '-a', '--add_currency', action='store_true',
        help='add target\'s currency code to result'
    )
    return parser

def run(args):
    if args.list_codes:
        print(*get_currency_codes(), sep=',')
    else:
        conversions = args.conversions or stdin
        try:
            for conv in conversions:
                print(convert_string(conv, args.precision, args.add_currency))
        except KeyboardInterrupt:
            print('')

def main(arguments=None):
    parser = get_argument_parser()
    try:
        run(parser.parse_args(arguments))
    except Exception as e:
        parser.error(e)
