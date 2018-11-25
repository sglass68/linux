# SPDX-License-Identifier: GPL-2.0+
#
# Rockchip platforms device tree bindings
#
# Copyright 2018 Google LLC
#

from kschema import NodeModel

schema = [
    NodeModel('Digilent Zybo board',
              ['adapteva,parallella',
              'digilent,zynq-zybo',
              'digilent,zynq-zybo-z7',
              'xlnx,zynq-cc108',
              'xlnx,zynq-zc702',
              'xlnx,zynq-zc706',
              'xlnx,zynq-zc770-xm010',
              'xlnx,zynq-zc770-xm011',
              'xlnx,zynq-zc770-xm012',
              'xlnx,zynq-zc770-xm013',
              'xlnx,zynq-7000',
    ]),
]
