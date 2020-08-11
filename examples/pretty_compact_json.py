# The MIT License (MIT)

# Copyright (c) 2014, 2016, 2017, 2019 Simon Lydell

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

# Based on https://github.com/lydell/json-stringify-pretty-compact/blob/master/index.js
# Ported to Python by CCCode

import re
import json

# The note below is from the original JavaScript code.
# JSON.stringify is the JS equivalent of json.dumps.

# Note: This regex matches even invalid JSON strings, but since we’re
# working on the output of `JSON.stringify` we know that only valid strings
# are present (unless the user supplied a weird `options.indent` but in
# that case we don’t care since the output would be invalid anyway).
string_or_char = '("(?:[^\\"]|\\.)*")|[:,]'

def stringify(passedObj, indent=2, max_length=80):
  # The original code supports a replacer function/array, but for now it's
  # not implemented here.

  indent_str = ' ' * indent

  if indent == 0:
    max_length = float('inf')

  def _stringify(obj, current_indent, reserved):
    # The original code checks if obj has a toJSON function here and uses that
    # to convert obj to JSON before continuing. It's not really necessary for
    # what I use this function for, so I decided to just remove it.

    string = json.dumps(obj, separators=(',', ':'))

    length = max_length - len(current_indent) - reserved

    if len(string) <= length:
      prettified = re.sub(string_or_char, lambda m: m.group(1) or m.group() + ' ', string)
      if len(prettified) <= length:
        return prettified

    if isinstance(obj, dict) or isinstance(obj, list):
      next_indent = current_indent + indent_str
      items = []

      if isinstance(obj, dict):
        start = '{'
        end = '}'
        keys = list(obj.keys())
        length = len(keys)
        for index in range(length):
          key = keys[index]
          key_part = json.dumps(key, separators=(',', ':')) + ': '
          value = _stringify(obj[key], next_indent, len(key_part) + (0 if index == length - 1 else 1))
          if not value is None:
            items.append(key_part + value)

      else: # obj is list
        start = '['
        end = ']'
        length = len(obj)
        for index in range(length):
          items.append(_stringify(obj[index], next_indent, 0 if index == length - 1 else 1) or 'null')

      if len(items) > 0:
        return f'\n{current_indent}'.join([start, indent_str + f',\n{next_indent}'.join(items), end])

    return string

  return _stringify(passedObj, '', 0)