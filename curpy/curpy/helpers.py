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
import os

from datetime import date, datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
from urllib.request import urlopen
from xml.etree import ElementTree as etree

EUROFXREF_URL = 'https://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml'

JSON_FILENAME = os.path.join('data', 'rates.json')

UPDATE_HOUR, UPDATE_MINUTE = (16, 0)

def _convert(data, rate_converter, date_converter):
    rates = {k: rate_converter(v) for k, v in data['rates'].items()}
    return {'rates': rates, 'date': date_converter(data['date'])}

def save_to_json(data, filename=JSON_FILENAME):
    converted = _convert(data, float, str)
    with open(filename, 'w') as stream:
        json.dump(converted, stream)

def load_json_rates(filename=JSON_FILENAME, must_exist=True):
    try:
        with open(filename) as stream:
            data = json.load(stream)
    except FileNotFoundError:
        if not must_exist:
            return {}
        raise
    return _convert(data, Decimal, date.fromisoformat)

def load_ecb_rates(url=EUROFXREF_URL, fallback=None):
    try:
        with urlopen(url) as stream:
            tree = etree.parse(stream)
    except OSError:
        if not fallback:
            raise
        return fallback
    return _ecb_to_json(tree)

def _ecb_to_json(tree):
    rates = {'EUR': Decimal(1)}
    for elem in tree.iterfind('.//*[@rate]'):
        rates[elem.get('currency')] = Decimal(elem.get('rate'))
    isodate = tree.find('.//*[@time]').get('time')
    return {'rates': rates, 'date': date.fromisoformat(isodate)}

def _is_outdated(data, filename, hour=UPDATE_HOUR, minute=UPDATE_MINUTE):
    now = datetime.now()
    if data['date'] != now.date():
        last_update = now.replace(hour=hour, minute=minute, second=0)
        if (hour, minute) > (now.hour, now.minute):
            # Update time not reached -> Use yesterday
            last_update -= timedelta(days=1)
        if last_update.isoweekday() > 5:
            # Date is weekend -> Use last Friday
            last_update -= timedelta(days=last_update.isoweekday() - 5)
        file_modified = datetime.fromtimestamp(os.stat(filename).st_mtime)
        return last_update > file_modified
    return False

def load_update(filename=JSON_FILENAME):
    data = load_json_rates(filename, must_exist=False)
    if not data or _is_outdated(data, filename):
        ecb_data = load_ecb_rates(fallback=data)
        if ecb_data != data:
            save_to_json(ecb_data, filename)
            return ecb_data
    return data

def get_formatted(number, precision=2):
    d = Decimal(number)
    if precision < 0:
        raise ValueError('precision must not be negative')
    exp = Decimal(10) ** -precision
    rounded = d.quantize(exp, rounding=ROUND_HALF_UP)
    return str(rounded)
