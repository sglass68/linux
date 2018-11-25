# SPDX-License-Identifier: GPL-2.0+
#
# Rockchip platforms device tree bindings
#
# Copyright 2018 Google LLC
#

from kschema import NodeModel

schema = [
    NodeModel('Google Jerry',
              ['google,veyron-jerry-rev7', 'google,veyron-jerry-rev6',
               'google,veyron-jerry-rev5', 'google,veyron-jerry-rev4',
               'google,veyron-jerry-rev3', 'google,veyron-jerry',
               'google,veyron', 'rockchip,rk3288']),
]
