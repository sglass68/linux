# SPDX-License-Identifier: GPL-2.0+
#
# /memory bindings
#
# Copyright 2018 Google LLC
#

from kschema import NodeMemory, PropReg, PropString

schema = [
    NodeMemory([
        PropString('device_type', True),
        PropReg(),
    ]),
]
