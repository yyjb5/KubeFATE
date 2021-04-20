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

from .fate_model import FATEModel


def get_trained_model(type="fate", **kwargs):
    """Generate a TrainedModel object from the input parameters

    Refer to the FATEModel doc for details about supported kwargs.

    :param type: the model type, defaults to "fate"
    :type type: str, optional
    :returns: a TrainedModel object
    :rtype: subclass of TrainedModel
    :raises: ValueError
    """
    if type.lower() == "fate":
        return FATEModel(**kwargs)
    else:
        raise ValueError("unknown model type: {}".format(type))
