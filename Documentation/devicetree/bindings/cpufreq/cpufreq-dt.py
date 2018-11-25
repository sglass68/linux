# SPDX-License-Identifier: GPL-2.0+
#
# /cpu bindings
#
# Copyright 2018 Google LLC
#

from kschema import NodeCpu
from kschema import PropInt

schema1 = [
    NodeCpu(None, [
        PropInt('clock-latency'),
        ])
    ]
