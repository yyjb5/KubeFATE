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

from enum import Enum

from .base import BaseModelStorage
from .minio import MinIOModelStorage


class ModelStorageType(Enum):
    LOCAL_FILE = 1
    MINIO = 2


def get_model_storage(storage_type=ModelStorageType.LOCAL_FILE, **kwargs):
    if storage_type == ModelStorageType.LOCAL_FILE:
        return BaseModelStorage(**kwargs)
    elif storage_type == ModelStorageType.MINIO:
        return MinIOModelStorage(**kwargs)
    else:
        raise ValueError("unknown model storage type: {}".format(storage_type))
