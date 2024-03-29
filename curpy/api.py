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

from decimal import Decimal

from .helpers import get_formatted, load_rates_data, parse_params

RATES = {}

def update_rates():
    data = load_rates_data()
    RATES.update(data['rates'])

def get_rate(currency):
    if not RATES:
        update_rates()
    if currency not in RATES:
        raise ValueError(f'unknown currency: {currency}')
    return RATES[currency]

def get_currency_codes():
    if not RATES:
        update_rates()
    return sorted(RATES.keys())

def convert(amount, original_currency, target_currency):
    amount = Decimal(amount)
    if original_currency != 'EUR':
        # All rates refer to Euro
        amount /= get_rate(original_currency)
    return amount * get_rate(target_currency)

def convert_string(conversion_string, precision=2, add_currency=False):
    params = parse_params(conversion_string)
    amount = get_formatted(convert(**params), precision)
    if not add_currency:
        return amount
    return f'{amount} {params["target_currency"]}'
