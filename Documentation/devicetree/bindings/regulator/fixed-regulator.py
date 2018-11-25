# SPDX-License-Identifier: GPL-2.0+
#
# Performance-Monitoring Unit (PMU) bindings
#
# not Copyright 2018 Google LLC
#

from kschema import NodeDesc, PropString
from regulator import SCHEMA_REGULATOR

schema = [
    NodeDesc('regulator-fixed', ['regulator-fixed'], False, [
    ] + SCHEMA_REGULATOR),
]
