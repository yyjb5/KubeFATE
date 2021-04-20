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

from ruamel import yaml

# XXX: federatedml dependency
import federatedml

from .trained_model import TrainedModel
from ..integration.fate import FATEFlowClient


logger = logging.getLogger(__name__)

SUPPORTED_MODELS = ['HomoLR', 'HomoNN']


class FATEModel(TrainedModel):
    """Class representing model from FATE project

    If model_dict is provided, this model will use the dict directly.
    The preferred framework is inferred from the model metadata.
    """
    def __init__(self,
                 model_path=None,
                 model_dict=None,
                 model_version=None,
                 fate_flow_host=None,
                 fate_flow_port=None,
                 api_version="v1",
                 role="guest",
                 party_id=None,
                 model_id=None):
        """
        :param model_path: path to the local model folder, defaults to None
        :type model_path: str, optional
        :param model_dict: the dict of the model data, defaults to None
        :type model_dict: dict, optional
        :param model_version: model version recorded in fate flow, defaults to None
        :type model_version: str, optional
        :param fate_flow_host: fate flow server host address, defaults to None
        :type fate_flow_host: str, optional
        :param fate_flow_port: fate flow server port, defaults to None
        :type fate_flow_port: int, optional
        :param api_version: defaults to "v1"
        :type api_version: str, optional
        :param role: role of the party, defaults to "guest"
        :type role: str, optional
        :param party_id: party id of the model, defaults to None
        :type party_id: int, optional
        :param model_id: id of the model, defaults to ""
        :type model_id: str, optional
        """
        super(FATEModel, self).__init__()
        self.type = "FATE"
        self.model_path = model_path
        self.model_dict = model_dict
        self.model_version = model_version
        self.fate_flow_client = FATEFlowClient(fate_flow_host, fate_flow_port, api_version)
        self.role = role
        self.party_id = party_id
        self.model_id = model_id
        self._do_init()

    def _need_download(self):
        return not self.model_dict and not self.model_path

    def _download(self):
        if self._need_download():
            self.model_path = self.fate_flow_client.fetch_fate_model(self.model_version,
                                                                     self.role,
                                                                     self.party_id,
                                                                     self.model_id)
        return self.model_path

    def get_all_components(self):
        with open(self.define_meta_path, "r", encoding="utf-8") as fr:
            define_index = yaml.safe_load(fr)
            model_proto_type = define_index.get("component_define", {})
            result = []
            for name in model_proto_type:
                result.append({
                    'name': name,
                    'type': model_proto_type[name]['module_name']
                })
            return result

    def preferred_framework(self):
        return self._target_framework

    def _do_init(self):
        """perform necessary initialization from the specified model info
        to get the model_dict data
        """
        if not self.model_dict:
            if not self.model_path:
                if not self.model_version:
                    raise ValueError("missing model_dict, model_path and model_version to locate FATE mode")
                self.model_path = self._download()
            self.define_proto_path = os.path.join(self.model_path, "define", "proto")
            self.define_meta_path = os.path.join(self.model_path, "define", "define_meta.yaml")
            self.variables_index_path = os.path.join(self.model_path, "variables", "index")
            self.variables_data_path = os.path.join(self.model_path, "variables", "data")
            for component in self.get_all_components():
                if component['type'] in SUPPORTED_MODELS:
                    self.model_dict = self._read_component(component['name'])

        if self.model_dict is None:
            raise RuntimeError('unable to find component as the main model')

        if self.model_dict['type'] == "HomoLR":
            self._target_framework = "sklearn"
        elif self.model_dict['type'] == 'HomoNN':
            if self.model_dict['NNModelMeta'].params.config_type == "pytorch":
                self._target_framework = "pytorch"
            else:
                self._target_framework = "tf_keras"
        else:
            raise RuntimeError("unknown component type: {}".format(self.model_dict['type']))
        logger.info("FATEModel initialized with component type: {} and target framework: {}".
                    format(self.model_dict['type'], self._target_framework))

    def _read_component(self, component_name, model_alias="model"):
        component_model_storage_path = os.path.join(self.variables_data_path, component_name, model_alias)
        with open(self.define_meta_path, "r", encoding="utf-8") as fr:
            define_index = yaml.safe_load(fr)
            model_proto_type = define_index.get("component_define", {}).get(component_name, {}).get("module_name")
            model_proto_index = define_index.get("model_proto", {}).get(component_name, {}).get(model_alias, {})
            model_buffers = {"type": model_proto_type}
            for model_name, buffer_name in model_proto_index.items():
                with open(os.path.join(component_model_storage_path, model_name), "rb") as f:
                    buffer_object_serialized_string = f.read()
                    model_buffers[buffer_name] =\
                        self._parse_proto_object(buffer_name=buffer_name,
                                                 buffer_object_serialized_string=buffer_object_serialized_string)
            return model_buffers

    @staticmethod
    def _parse_proto_object(buffer_name, buffer_object_serialized_string):
        buffer_object = FATEModel._get_proto_buffer_class(buffer_name)()
        buffer_object.ParseFromString(buffer_object_serialized_string)
        return buffer_object

    @staticmethod
    def _get_proto_buffer_class(buffer_name):
        package_path = os.path.join(federatedml.__path__[0], 'protobuf', 'generated')
        package_python_path = 'federatedml.protobuf.generated'
        for f in os.listdir(package_path):
            if f.startswith('.'):
                continue
            proto_module = importlib.import_module(package_python_path + '.' + f.rstrip('.py'))
            for name, obj in inspect.getmembers(proto_module):
                if inspect.isclass(obj) and name == buffer_name:
                    return obj
