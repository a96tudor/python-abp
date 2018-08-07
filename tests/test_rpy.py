# This file is part of Adblock Plus <https://adblockplus.org/>,
# Copyright (C) 2006-present eyeo GmbH
#
# Adblock Plus is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3 as
# published by the Free Software Foundation.
#
# Adblock Plus is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Adblock Plus.  If not, see <http://www.gnu.org/licenses/>.

"""Functional tests for testing rPython integration."""
from __future__ import unicode_literals

from collections import namedtuple
import pytest

from abp.filters.rpy import (
    tuple2dict, line2dict,
)

_SAMPLE_TUPLE = namedtuple('tuple', 'foo,bar')

_ENCODED_STR_TYPE = type(''.encode('utf-8'))

_EXPECTED_TYPES = {
    'header': {
        'type': _ENCODED_STR_TYPE,
        'version': _ENCODED_STR_TYPE,
    },
    'metadata': {
        'type': _ENCODED_STR_TYPE,
        'key': _ENCODED_STR_TYPE,
        'value': _ENCODED_STR_TYPE,
    },
    'empty': {
        'type': _ENCODED_STR_TYPE,
    },
    'comment': {
        'type': _ENCODED_STR_TYPE,
        'text': _ENCODED_STR_TYPE,
    },
    'include': {
        'type': _ENCODED_STR_TYPE,
        'target': _ENCODED_STR_TYPE,
    },
    'filter': {
        'type': _ENCODED_STR_TYPE,
        'text': _ENCODED_STR_TYPE,
        'selector': dict,
        'action': _ENCODED_STR_TYPE,
        'options': list,
    },
}


def check_correct_datatypes(data, expected_types):
    """Check if the resulting data has the correct keys and datatypes.

    Parameters
    ----------
    data: dict
        The dictonary produced by the API

    expected_types: dict
        The expected keys and datatypes associated with them.

    Raises
    -------
    AssertionError
        If any of the types/ keys don't correspond

    """
    def encode_fn(x):
        return x.encode('utf-8')

    data_keys = sorted(list(data.keys()))
    expected_keys = sorted(list(map(encode_fn, expected_types.keys())))

    if data_keys != expected_keys:
        raise AssertionError('Invalid dict format. Got keys {0}, '
                             'expected {1}'.format(data_keys, expected_keys))

    for key in data:
        if not isinstance(data[key], expected_types[key.decode('utf-8')]):
            raise AssertionError(
                'Invalid dict format. {0} should be {1}. Got {2}'.format(
                    key,
                    expected_types[key.decode('utf-8')],
                    type(data[key]),
                ),
            )


def check_data_utf8(data):
    """Check if all the strings in a dict are encoded as unicode.

    Parameters
    ----------
    data: dict
        The dictionary to be checked

    Raises
    -------
    AssertionError
        If any of the strings encountered are not unicode

    """
    if isinstance(data, dict):
        for key, value in data.items():
            check_data_utf8(key)
            check_data_utf8(value)
    elif isinstance(data, (list, tuple)):
        for item in data:
            check_data_utf8(item)
    elif isinstance(data, type('')):
        raise AssertionError('{} is str. Expected bytes.'.format(data))


@pytest.mark.parametrize('foo,bar', [
    ('test_foo', 1),
    ({'foofoo': 'test', 'foobar': 2}, [1, 2, 3]),
    ((1,), [('a', True), ('b', False)]),
])
def test_tuple2dict(foo, bar):
    """Test that dicts are produced correctly from a named tuple."""
    data = _SAMPLE_TUPLE(foo=foo, bar=bar)
    exp = {'foo': foo, 'bar': bar, 'type': 'tuple'}

    result = tuple2dict(data)

    assert exp == result


@pytest.mark.parametrize('filter_text', [
    'abc$image',
    '\u0432\u0435\u0431\u0441\u0430\u0439.\u0440\u0444$domain=\xfcber.de',
])
def test_line2dict_encoding(filter_text):
    """Test that the resulting object has all strings encoded as utf-8."""
    data = line2dict(filter_text.encode('utf-8'))
    check_data_utf8(data)


@pytest.mark.parametrize('line,expected', [
    ('[Adblock Plus 2.0]', _EXPECTED_TYPES['header']),
    ('! Title: Example list', _EXPECTED_TYPES['metadata']),
    ('! Comment', _EXPECTED_TYPES['comment']),
    ('abc.com,cdf.com##div#ad1', _EXPECTED_TYPES['filter']),
    ('%include www.test.py/filtelist.txt%', _EXPECTED_TYPES['include']),
    ('', _EXPECTED_TYPES['empty']),
])
def test_line2dict_format(line, expected):
    """Test that the API result has the appropriate format.

    Checks for both keys and datatypes.
    """
    data = line2dict(line)
    check_correct_datatypes(data, expected)
