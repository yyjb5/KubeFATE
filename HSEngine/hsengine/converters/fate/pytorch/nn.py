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

import io

import torch

from ..component_converter import ComponentConverterBase


class NNComponentConverter(ComponentConverterBase):

    @staticmethod
    def get_target_modules():
        return ['HomoNN']

    def convert(self, fate_component_dict):
        param_obj = fate_component_dict["NNModelParam"]
        meta_obj = fate_component_dict["NNModelMeta"]
        if meta_obj.params.config_type != "pytorch":
            raise ValueError("Invalid config type: {}".format(meta_obj.config_type))

        with io.BytesIO(param_obj.saved_model_bytes) as model_bytes:
            if hasattr(param_obj, "api_version") and param_obj.api_version > 0:
                # XXX federatedml is not in the PyPI
                from federatedml.nn.homo_nn._torch import FedLightModule
                pytorch_nn_model = FedLightModule.load_from_checkpoint(model_bytes).model
            else:
                pytorch_nn_model = torch.load(model_bytes)
            return pytorch_nn_model
