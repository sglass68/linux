# SPDX-License-Identifier: GPL-2.0+
#
# Performance-Monitoring Unit (PMU) bindings
#
# not Copyright 2018 Google LLC
#

from kschema import NodeDesc, PropGpios, PropInt, PropPhandleTarget

schema = [
    NodeDesc('usb-nop-xceiv', ['usb-nop-xceiv'], False, [
        PropPhandleTarget(),
        PropInt('#phy-cells'),
        PropGpios('reset', 1),
    ]),
]
