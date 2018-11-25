# SPDX-License-Identifier: GPL-2.0+
#
# base (built-in) bindings
#
# Copyright 2018 Google LLC
#

from kschema import NodeDesc, PropBool

schema = [
    NodeDesc('simple-bus', ['simple-bus'], False, [
        PropBool('ranges'),
    ]),
]
