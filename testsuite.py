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

import unittest

from contextlib import redirect_stderr, redirect_stdout
from decimal import Decimal
from io import StringIO

from curpy import api, cli

class CLITest(unittest.TestCase):
    def send_command(self, *args):
        output = StringIO()
        with redirect_stdout(output):
            cli.main(args)
        return output.getvalue().rstrip()

    def send_invalid_command(self, *args):
        errors = StringIO()
        with redirect_stderr(errors):
            try:
                cli.main(args)
            except SystemExit:
                return errors.getvalue().rstrip()
            else:
                self.fail('expected program exit')

    def test_list_codes(self):
        for arg in ('-l', '--list-codes'):
            with self.subTest(arg=arg):
                codes = self.send_command(arg).split(',')
                self.assertEqual(codes, api.get_currency_codes())

    def test_conversions(self):
        single_conversion = '1 EUR in USD'
        two_conversions = ['0.319 USD in GBP', '5.99 CNY in JPY']
        amount = self.send_command(single_conversion)
        self.assertEqual(amount, api.convert_string(single_conversion))
        amounts = self.send_command(*two_conversions).split('\n')
        expected = [api.convert_string(conv) for conv in two_conversions]
        self.assertEqual(amounts, expected)

    def test_invalid_conversions(self):
        for string in ('', ' ', 'SPAM', '42 SPAM in EGGS'):
            with self.subTest(string=string):
                output = self.send_invalid_command(string)
                self.assertRegex(output, 'invalid string format')
        output = self.send_invalid_command('1 EUR in XXX')
        self.assertRegex(output, 'unknown currency')


if __name__ == '__main__':
    unittest.main(verbosity=2)
