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

class DeployerBase(object):
    """Base class for an deployer

    A deployer is in charge of deploying a model into a serving service
    running in the target cluster.
    """

    def __init__(self, service_name, version, converted_model):
        self.service_name = service_name
        self.version = version
        self.converted_model = converted_model

    def deploy(self):
        raise NotImplementedError("deploy method not implemented")

    def destroy(self):
        raise NotImplementedError("destroy method not implemented")

    def status(self):
        raise NotImplementedError("status method not implemented")
