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

import pytest

from hsengine.converters.converter_base import ConvertedModel
from hsengine.deployers import get_deployer
from hsengine.deployers.kfserving.base import KFServingDeployer


@pytest.fixture(scope="session")
def converted_model(tmp_path_factory):
    return ConvertedModel("sklearn", object())


def test_deployer(converted_model, monkeypatch):
    deployer = get_deployer(service_name="dummy service",
                            version="0.1",
                            model=converted_model)
    assert isinstance(deployer, KFServingDeployer)

    # assert the storage uri is properly generated
    monkeypatch.setattr(deployer.model_storage,
                        "save",
                        lambda *args, **kwargs: "s3://dummy_path")
    storage_path = deployer.prepare_model()
    assert storage_path == "s3://dummy_path"

    # assert the isvc's storage uri is properly set
    def mock_not_found():
        raise RuntimeError("Reason: Not Found")
    monkeypatch.setattr(deployer.kfserving_client,
                        "get",
                        lambda *args, **kwargs: mock_not_found())
    monkeypatch.setattr(deployer.kfserving_client,
                        "create",
                        lambda *args, **kwargs: object())
    deployer.deploy()
    assert deployer.isvc.spec.predictor.sklearn.storage_uri == storage_path
