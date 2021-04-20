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

import base64
import io
import os
import zipfile

import pytest

from hsengine.trained_model.fate_model import FATEModel
from hsengine.trained_model import get_trained_model
from hsengine.integration.fate.fate_client import FATEFlowClient


@pytest.fixture(scope="session")
def downloaded_model(tmp_path_factory):
    with open(os.path.join(os.path.dirname(__file__), "mock_model_data"), "r") as fh:
        model_file_bytes = base64.b64decode(fh.read())
    temp_dir = tmp_path_factory.mktemp("model")
    with io.BytesIO(model_file_bytes) as bytes_io:
        with zipfile.ZipFile(bytes_io, 'r', zipfile.ZIP_DEFLATED) as f:
            f.extractall(temp_dir)
    return str(temp_dir)


def test_get_trained_model(downloaded_model, monkeypatch):
    monkeypatch.setattr(FATEFlowClient, "fetch_fate_model", lambda *args, **kwargs: downloaded_model)
    model = get_trained_model(model_version="dummy version")
    assert type(model) == FATEModel
    assert model.preferred_framework() == "sklearn"
