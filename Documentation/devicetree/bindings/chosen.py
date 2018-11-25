# SPDX-License-Identifier: GPL-2.0+
#
# /chosen bindings
#
# Copyright 2018 Google LLC
#

from kschema import NodeChosen, PropString

schema = [
    NodeChosen([
        PropString('bootargs'),
        PropString('stdout-path'),
    ]),
]
