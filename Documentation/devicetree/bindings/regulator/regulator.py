# SPDX-License-Identifier: GPL-2.0+
#
# Performance-Monitoring Unit (PMU) bindings
#
# not Copyright 2018 Google LLC
#

from kschema import NodeDesc, PropBool, PropInt, PropPhandleTarget, PropString

SCHEMA_REGULATOR = [
    PropString('regulator-name', True),
    PropBool('regulator-always-on'),
    PropBool('regulator-boot-on'),
    PropInt('regulator-min-microvolt'),
    PropInt('regulator-max-microvolt'),
    PropPhandleTarget(),
    ];

no_schema = True
