# SPDX-License-Identifier: GPL-2.0+
#
# fpga-region bindings
#
# Copyright 2018 Google LLC
#

from kschema import NodeDesc, PropBool, PropPhandle

schema = [
    NodeDesc('fpga-region', ['fpga-region'], True, [
        PropPhandle('fpga-mgr', 'xlnx,zynq-devcfg-1.0'),
        PropBool('ranges'),
    ]),
]
