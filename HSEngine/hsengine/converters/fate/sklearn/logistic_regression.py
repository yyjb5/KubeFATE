# Copyright 2021 VMware, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# you may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import numpy as np
from sklearn.linear_model import LogisticRegression

from ..component_converter import ComponentConverterBase


class LRComponentConverter(ComponentConverterBase):

    @staticmethod
    def get_target_modules():
        return ['HomoLR']

    def convert(self, fate_component_dict):
        param_obj = fate_component_dict["LRModelParam"]

        sk_lr_model = LogisticRegression()

        coefficient = np.empty((1, len(param_obj.header)))
        for index in range(len(param_obj.header)):
            coefficient[0][index] = param_obj.weight[param_obj.header[index]]

        sk_lr_model.coef_ = coefficient

        intercept = np.array([param_obj.intercept])
        sk_lr_model.intercept_ = intercept

        # hard-coded 0-1 classification as FATE HomoLR only supports this
        # for now
        sk_lr_model.classes_ = np.array([0., 1.])
        return sk_lr_model
