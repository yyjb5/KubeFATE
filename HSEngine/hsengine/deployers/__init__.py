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

from .kfserving import get_kfserving_deployer


def get_deployer(service_name, version, model, type="kfserving", **kwargs):
    """Returns a deployer instance based on the specified type

    Refer to the doc of KFServingDeployer and get_kfserving_deployer for
    details about supported kwargs.

    :param service_name: service name representing the deployed instance
    :type service_name: str
    :param version: version string of the deployed service
    :type version: str
    :param model: the converted model instance
    :type model: ConvertedModel
    :param type: the deployer type, defaults to "kfserving"
    :type type: str, optional
    :returns: an instance of DeployerBase
    :rtype: a subclass of DeployerBase
    :raises: ValueError
    """
    if type == "kfserving":
        return get_kfserving_deployer(service_name, version, model, **kwargs)
    else:
        raise ValueError("unknown deployer type: {}".format(type))
