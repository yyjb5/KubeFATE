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

from hsengine.integration.model_storage import get_model_storage, ModelStorageType
from hsengine.integration.model_storage.minio import MinIOModelStorage


def test_minio_storage(monkeypatch):
    minio_storage = get_model_storage(ModelStorageType.MINIO,
                                      framework="sklearn",
                                      sub_path="dummy_sub_path")
    assert isinstance(minio_storage, MinIOModelStorage)

    def no_op_mock():
        return True

    monkeypatch.setattr(minio_storage.client,
                        "fput_object",
                        lambda *args, **kwargs: no_op_mock())
    monkeypatch.setattr(minio_storage.client,
                        "bucket_exists",
                        lambda *args, **kwargs: no_op_mock())
    uri = minio_storage.upload_objects([
        {
            "dest": "dummy_dest_1",
            "obj": "dummy_path_1"
        },
        {
            "dest": "dummy_dest_1",
            "obj": "dummy_path_2"
        }
    ])
    assert uri == "s3://models/dummy_sub_path"
