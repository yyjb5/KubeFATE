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

from hsengine.trained_model import get_trained_model
from hsengine.converters import get_converter
from hsengine.converters.fate.fate_converter import FATEConverter


@pytest.fixture(scope="session")
def fate_model(tmp_path_factory):
    with open(os.path.join(os.path.dirname(__file__), "mock_model_data"), "r") as f:
        model_file_bytes = base64.b64decode(f.read())
    temp_dir = tmp_path_factory.mktemp("model")
    with io.BytesIO(model_file_bytes) as bytes_io:
        with zipfile.ZipFile(bytes_io, 'r', zipfile.ZIP_DEFLATED) as f:
            f.extractall(temp_dir)
    return get_trained_model(model_path=temp_dir)


def test_get_converter(fate_model, monkeypatch):
    converter = get_converter(fate_model)
    assert type(converter) == FATEConverter
    converted_model = converter.convert()
    assert converted_model.framework == "sklearn"
