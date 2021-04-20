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

from .pytorch import TorchServeKFDeployer
from .sklearn import SKLearnV1KFDeployer, SKLearnV2KFDeployer
from .tensorflow import TFServingKFDeployer


def get_kfserving_deployer(service_name, version, converted_model,
                           protocol_version="v1", **kwargs):
    """Returns a deployer for KFServing InferenceService

    The returned deployer should be a specific one for the framework used
    in the converted_model. Refer to KFServingDeployer and its sub-classes
    for supported kwargs.

    :param service_name: name of the service
    :type service_name: str
    :param version: version string
    :type version: str
    :param converted_model: the converted model
    :type converted_model: ConvertedModel
    :param protocol_version: supported protocol version, defaults to "v1"
    :type protocol_version: str, optional
    """
    framework = converted_model.framework
    if framework in ['sklearn', 'scikit-learn']:
        if protocol_version == "v2":
            cls = SKLearnV2KFDeployer
        else:
            cls = SKLearnV1KFDeployer
    elif framework in ['pytorch', 'torch']:
        cls = TorchServeKFDeployer
    elif framework in ['tf_keras', 'tensorflow', 'tf']:
        cls = TFServingKFDeployer
    else:
        raise ValueError("unknown converted model framework: {}".format(framework))
    return cls(service_name, version, converted_model, **kwargs)
