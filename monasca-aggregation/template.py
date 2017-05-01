#!/usr/bin/env python

# (C) Copyright 2017 Hewlett Packard Enterprise Development LP
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
from __future__ import print_function

import os
import sys

from jinja2 import Template


def main():
    if len(sys.argv) != 3:
        print('Usage: {} [input] [output]'.format(sys.argv[0]))
        sys.exit(1)

    in_path = sys.argv[1]
    out_path = sys.argv[2]

    with open(in_path, 'r') as in_file, open(out_path, 'w') as out_file:
        t = Template(in_file.read(),
                     keep_trailing_newline=True,
                     lstrip_blocks=True,
                     trim_blocks=True)
        out_file.write(t.render(os.environ))

if __name__ == '__main__':
    main()
