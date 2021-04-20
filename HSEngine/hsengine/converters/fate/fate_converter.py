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

import importlib
import inspect
import logging
import os

from .component_converter import ComponentConverterBase
from ..converter_base import ConverterBase, ConvertedModel
from ...integration.model_storage import ModelStorageType


logger = logging.getLogger(__name__)


class FATEConverter(ConverterBase):
    """Converter class to convert FATE model into format of common ML frameworks

    A FATE converter depends on the TrainedModel's preferred_framework() result
    to find the appropriate component converter to convert the FATE component
    into the common framework model.
    """

    def __init__(self,
                 trained_model,
                 model_storage_type=ModelStorageType.LOCAL_FILE,
                 model_storage_kwargs=None):
        super().__init__(trained_model, model_storage_type, model_storage_kwargs)
        self.component_converter = self.get_component_converter()
        logger.debug("Initialized FATEConverter with {}".format(type(self.component_converter)))

    def convert(self):
        if self.trained_model.model_dict is None:
            raise RuntimeError("missing model dict data")

        self.converted_model = ConvertedModel(self.trained_model.preferred_framework(),
                                              self.component_converter.convert(
                                                    self.trained_model.model_dict))
        return self.converted_model

    def get_component_converter(self):
        framework_name = self.trained_model.preferred_framework()
        if framework_name in ["tensorflow", "tf", "tf_keras"]:
            framework_name = "tf_keras"
        elif framework_name in ["pytorch", "torch"]:
            framework_name = "pytorch"
        elif framework_name in ["sklearn", "scikit-learn"]:
            framework_name = "sklearn"
        package_name = "." + framework_name
        parent_package = importlib.import_module(package_name, __package__)
        parent_package_path = os.path.dirname(os.path.realpath(parent_package.__file__))
        model_type = self.trained_model.model_dict['type']
        for f in os.listdir(parent_package_path):
            if f.startswith('.') or f.startswith('_'):
                continue
            if not f.endswith('.py'):
                continue
            proto_module = importlib.import_module("." + f.rstrip('.py'), parent_package.__name__)
            for name, obj in inspect.getmembers(proto_module):
                if inspect.isclass(obj) and issubclass(obj, ComponentConverterBase):
                    for module in obj.get_target_modules():
                        if module == model_type:
                            return obj()
        raise RuntimeError("cannot find component_converter for mode: {} in {}".format(model_type, framework_name))
