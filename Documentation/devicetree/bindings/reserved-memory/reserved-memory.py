# SPDX-License-Identifier: GPL-2.0+
#
# /reserved-memory bindings
#
# Copyright 2018 Google LLC
#

from kschema import NodeReservedMemory, PropBool

schema = [
    NodeReservedMemory([
        PropBool('ranges'),
    ]),
]
