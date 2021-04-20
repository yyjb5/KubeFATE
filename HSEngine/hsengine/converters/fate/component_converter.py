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

class ComponentConverterBase(object):
    """Base class representing a component converter

    A component converter expects a dict in FATE's model dict format that
    contains "type", "XXXMeta" and "XXXParams" values. One can use FATEModel's
    _read_component() method to inspect such dict content.
    """

    @staticmethod
    def get_target_modules():
        """Returns the FATE component module type that this converter supports.
        """
        return []

    def convert(self, fate_component_dict):
        return fate_component_dict
