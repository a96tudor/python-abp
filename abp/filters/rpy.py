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

"""
Functions for integrating with rPython.

see: https://cran.r-project.org/web/packages/rPython/index.html
"""

from __future__ import unicode_literals

from abp.filters import parse_line

__all__ = ['line2dict']


def tuple2dict(data):
    """Convert a parsed filter from a namedtuple to a dict.

    Parameters
    ----------
    filter: namedtuple
        The parsed filter.

    Returns
    -------
    dict
        The resulting dictionary

    """
    result = dict(data._asdict())
    result['type'] = data.__class__.__name__

    return result


def strings2utf8(data):
    """Convert strings in a data structure to utf8 byte strings.

    `data` can include nested dicts and lists.
    """
    if isinstance(data, dict):
        return {strings2utf8(k): strings2utf8(v) for k, v in data.items()}
    if isinstance(data, list):
        return [strings2utf8(v) for v in data]
    if isinstance(data, tuple):
        return tuple(strings2utf8(v) for v in data)
    if isinstance(data, type('')):  # Python 2/3 compatible way of
                                    # saying "unicode string".
        return data.encode('utf-8')
    return data


def line2dict(text):
    """Convert a filterlist line to a dictionary.

    All strings in the output dictionary will be UTF8 byte strings. This is
    necessary to prevent unicode encoding errors in rPython conversion layer.
    """
    return strings2utf8(tuple2dict(parse_line(text)))
