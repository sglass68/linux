# SPDX-License-Identifier: GPL-2.0+
#
# Performance-Monitoring Unit (PMU) bindings
#
# not Copyright 2018 Google LLC
#

from kschema import NodeDesc, PropIntList, PropReg

schema = [
    NodeDesc('pmu', [
        'apm,potenza-pmu',
        'arm,armv8-pmuv3',
        'arm,cortex-a73-pmu',
        'arm,cortex-a72-pmu',
        'arm,cortex-a57-pmu',
        'arm,cortex-a53-pmu',
        'arm,cortex-a35-pmu',
        'arm,cortex-a17-pmu',
        'arm,cortex-a15-pmu',
        'arm,cortex-a12-pmu',
        'arm,cortex-a9-pmu',
        'arm,cortex-a8-pmu',
        'arm,cortex-a7-pmu',
        'arm,cortex-a5-pmu',
        'arm,arm11mpcore-pmu',
        'arm,arm1176-pmu',
        'arm,arm1136-pmu',
        'brcm,vulcan-pmu',
        'cavium,thunder-pmu',
        'qcom,scorpion-pmu',
        'qcom,scorpion-mp-pmu',
        'qcom,krait-pmu',
        ], False, [
        PropReg(),
        PropIntList('interrupts'),
    ]),
]
