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

class TrainedModel(object):
    """Abstract class which serves as the main interface to trained FML models
    """
    def __init__(self):
        self.type = ""

    def preferred_framework(self):
        raise NotImplementedError("preferred_framework should be implemented in the derived class")
