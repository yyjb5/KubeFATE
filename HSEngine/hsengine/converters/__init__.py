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

from .fate.fate_converter import FATEConverter


def get_converter(trained_model, **kwargs):
    """Get the corresponding converter based on the trained model type

    Currently only FATE models are supported. Refer to the FATEConverter
    doc for supported kwargs.

    :param trained_model: the trained model
    :type trained_model: TrainedModel object
    :returns: the converter instance
    :rtype: subclass of ConverterBase
    :raises: ValueError
    """
    if trained_model.type.lower() == "fate":
        return FATEConverter(trained_model, **kwargs)
    else:
        raise ValueError("unknown trained model type: {}".format(trained_model.type))
