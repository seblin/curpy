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

import json

from datetime import date, datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
from os import getenv
from pathlib import Path
from sys import stderr
from urllib.request import urlopen
from xml.etree import ElementTree as etree

EUROFXREF_URL = 'https://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml'

UPDATE_HOUR, UPDATE_MINUTE = (16, 0)

def get_json_path(filename=None):
    if filename:
        return Path(filename)
    envdir = getenv('PROGRAMDATA') or getenv('HOME')
    if envdir:
        path = Path(envdir) / '.curpy'
    else:
        path = Path(__file__).parent / 'data'
    return path / 'rates.json'

def save_to_json(data, filename=None):
    path = get_json_path(filename)
    rates = {code: float(rate) for code, rate in data['rates'].items()}
    datestring = data['date'].isoformat()
    converted = {'rates': rates, 'date': datestring}
    if not path.parent.exists():
        path.parent.mkdir(parents=True)
    with path.open('w') as stream:
        json.dump(converted, stream)

def load_json_rates(filename=None):
    path = get_json_path(filename)
    try:
        with path.open() as stream:
            data = json.load(stream, parse_float=Decimal)
    except FileNotFoundError:
        # That's likely to occur on the first program start
        # No need to puzzle users with a message here :-)
        return {}
    parsed_date = date.fromisoformat(data['date'])
    return {'rates': data['rates'], 'date': parsed_date}

def load_ecb_rates(url=EUROFXREF_URL):
    try:
        with urlopen(url) as stream:
            tree = etree.parse(stream)
    except OSError as e:
        print(f'Failed to load ECB rates. You or {url!r} might be offline.',
              f'The original error message was: {e}', sep='\n', file=stderr)
        return {}
    return ecb_to_json(tree)

def ecb_to_json(tree):
    rates = {'EUR': Decimal('1.0')}
    for elem in tree.iterfind('.//*[@rate]'):
        rate = elem.get('rate').rstrip('0')
        rates[elem.get('currency')] = Decimal(rate)
    datestring = tree.find('.//*[@time]').get('time')
    parsed_date = date.fromisoformat(datestring)
    return {'rates': rates, 'date': parsed_date}

def is_outdated(data, hour=UPDATE_HOUR, minute=UPDATE_MINUTE):
    now = datetime.now()
    last_update = now.replace(hour=hour, minute=minute, second=0)
    if (hour, minute) > (now.hour, now.minute):
        # Update time not reached -> Use yesterday
        last_update -= timedelta(days=1)
    if last_update.isoweekday() > 5:
        # Date is weekend -> Use last Friday
        last_update -= timedelta(days=last_update.isoweekday() - 5)
    return last_update.date() > data['date']

def load_rates_data(filename=None):
    path = get_json_path(filename)
    json_data = load_json_rates(path)
    if not json_data or is_outdated(json_data):
        ecb_data = load_ecb_rates()
        if ecb_data:
            save_to_json(ecb_data, path)
            return ecb_data
    return json_data

def get_formatted(number, precision=2):
    d = Decimal(number)
    if precision < 0:
        raise ValueError('precision must not be negative')
    exp = Decimal(10) ** -precision
    rounded = d.quantize(exp, rounding=ROUND_HALF_UP)
    return str(rounded)
