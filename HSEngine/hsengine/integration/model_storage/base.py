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

import logging

logger = logging.getLogger(__name__)


class BaseModelStorage(object):
    def __init__(self, framework=""):
        self.framework = framework
        pass

    def save(self, model_object, dest):
        """Save the model into local file system
        :param dest: destination file/folder name
        :param model_object: the model object
        :return: local file/folder path
        """
        if self.framework.lower() in ["sklearn", "scikit-learn"]:
            import joblib
            joblib.dump(model_object, dest)
        elif self.framework.lower() in ["pytorch", "torch"]:
            import torch
            torch.save(model_object, dest)
        elif self.framework.lower() in ["tensorflow", "tf", "tf_keras"]:
            import tensorflow
            tensorflow.saved_model.save(model_object, dest)
        else:
            raise NotImplementedError("save method for framework: {} is not implemented"
                                      .format(self.framework))
        logger.info("Saved model of framework: {} into {}".format(self.framework, dest))
        return dest
