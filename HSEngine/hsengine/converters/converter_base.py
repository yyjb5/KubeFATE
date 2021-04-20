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

from ..integration.model_storage import get_model_storage, ModelStorageType

logger = logging.getLogger(__name__)


class ConverterBase(object):
    def __init__(self,
                 trained_model,
                 model_storage_type=ModelStorageType.LOCAL_FILE,
                 model_storage_kwargs=None):
        """
        :param trained_model: the trained model to be converted
        :param model_storage_type: type of the model storage for the converted model,
                                   defaults to ModelStorageType.LOCAL_FILE
        :param model_storage_kwargs: extra keyword arguments for the model storage instance.
                                     refer to the model storage classes for supported kwargs.
        """
        self.trained_model = trained_model
        self.converted_model = None
        if not model_storage_kwargs:
            model_storage_kwargs = {}
        logger.debug("With storage kwargs: {}".format(model_storage_kwargs))
        if model_storage_type == ModelStorageType.MINIO:
            from datetime import datetime
            sub_path = datetime.now().strftime("converted-model-%Y%m%d-%H%M%S")
            logger.info("Initialize MINIO model storage with sub path: {}, framework: {}"
                        .format(sub_path, trained_model.preferred_framework()))
            model_storage = get_model_storage(storage_type=model_storage_type,
                                              sub_path=sub_path,
                                              framework=trained_model.preferred_framework(),
                                              **model_storage_kwargs)
        else:
            model_storage = get_model_storage(storage_type=model_storage_type,
                                              framework=trained_model.preferred_framework(),
                                              **model_storage_kwargs)
        self.model_storage = model_storage

    def convert(self):
        raise NotImplementedError("convert method not implemented")

    def save_model(self, dest):
        if not self.converted_model:
            raise RuntimeError("model not converted yet")
        return self.model_storage.save(self.converted_model.model, dest)


class ConvertedModel(object):
    def __init__(self, framework, model):
        self.framework = framework
        self.model = model
