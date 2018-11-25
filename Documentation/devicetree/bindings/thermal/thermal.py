# SPDX-License-Identifier: GPL-2.0+
#
# /thermal-zone bindings
#
# Copyright 2018 Google LLC
#

from kschema import NodeDesc, NodeThermalZones

schema = [
    NodeThermalZones([
        NodeDesc('cpu-thermal', []),
        NodeDesc('gpu-thermal', []),
    ]),
]
