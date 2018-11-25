# SPDX-License-Identifier: GPL-2.0+
#
# operating-point bindings
#
# Copyright 2018 Google LLC
#

from kschema import NodeCpu
from kschema import PropIntList

schema1 = [
    NodeCpu(None, [
        PropIntList('operating-points'),
        ])
    ]
