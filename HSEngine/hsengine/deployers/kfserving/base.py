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
import uuid

import kfserving
from kfserving.api import creds_utils
from kubernetes import client

from ..deployer_base import DeployerBase
from ...integration.model_storage import get_model_storage, ModelStorageType
from ...integration.model_storage.minio import MinIOModelStorage

logger = logging.getLogger(__name__)

MINIO_KEY_PREFIX = "minio_"
MINIO_ENDPOINT_KEY = MINIO_KEY_PREFIX + "endpoint"
MINIO_ACCESS_KEY = MINIO_KEY_PREFIX + "access_key"
MINIO_SECRET_ACCESS_KEY = MINIO_KEY_PREFIX + "secret_key"
MINIO_SECURE_KEY = MINIO_KEY_PREFIX + "secure"
MINIO_REGION_KEY = MINIO_KEY_PREFIX + "region"
MINIO_K8S_SECRET_NAME = "hsengine-minio-secret"

STORAGE_URI_KEY = "storage_uri"

ANNOTATION_HSE_UUID = "hsengine.dev/uuid"


class KFServingDeployer(DeployerBase):
    """Class representing a KFServing service deployer
    """

    def __init__(self, service_name, version, converted_model,
                 namespace=None,
                 model_storage_type=ModelStorageType.MINIO,
                 storage_uri=None,
                 isvc=None,
                 kfserving_config=None,
                 replace=False,
                 share_storage_creds=True,
                 framework_kwargs=None,
                 model_storage_kwargs=None):
        """
        :param service_name: service name
        :type service_name: str
        :param version: version string
        :type version: str
        :param converted_model: the converted model to be deployed
        :type converted_model: ConvertedModel
        :param namespace: the kubernetes namespace this service belongs to
        :type namespace: str
        :param model_storage_type: type of the underlying model storage
                                   defaults to ModelStorageType.MINIO
        :type model_storage_type: enum ModelStorageType
        :param storage_uri: model storage url, defaults to None
        :type storage_uri: str, optional
        :param isvc: the InferenceService instance, defaults to None
        :type isvc: kfserving.V1beta1InferenceService, optional
        :param kfserving_config: kubernetes config file path, defaults to None
        :type kfserving_config: str, optional
        :param replace: whether to replace the running service, defaults to False
        :type replace: bool, optional
        :param share_storage_creds: whether or not to setup MinIO credentials for KFServing
                                    storage-initializer container, defaults to True.
        :param framework_kwargs: a dict containing extra arguments for use with
                                 framework specific logic, defaults to {}. See the
                                 doc of each Deployer classes for details about
                                 supported kwargs.
        :type framework_kwargs: dict, optional
        :param model_storage_kwargs: a dict containing extra arguments to initialize the
                                     model storage instance, defaults to {}.
                                     see the doc of model storage classes for the available
                                     parameters
        :type model_storage_kwargs: dict, optional
        """
        super(KFServingDeployer, self).__init__(service_name, version, converted_model)
        if framework_kwargs is None:
            framework_kwargs = {}
        if model_storage_kwargs is None:
            model_storage_kwargs = {}
        model_storage = get_model_storage(storage_type=model_storage_type,
                                          sub_path=service_name + "/" + version,
                                          framework=converted_model.framework,
                                          **model_storage_kwargs)
        self.framework_kwargs = framework_kwargs
        self.model_storage = model_storage
        self.storage_uri = storage_uri
        self.isvc = isvc
        # this should also set up kubernetes.client config
        self.kfserving_client = kfserving.KFServingClient(kfserving_config)
        self.namespace = namespace if namespace else kfserving.utils.get_default_target_namespace()
        self.replace = replace
        self.share_storage_creds = share_storage_creds
        self.created_isvc = None
        logger.debug("Initialized KFServingDeployer with client config: {}".format(kfserving_config))

    def prepare_model(self):
        if not self.storage_uri:
            self.storage_uri = self.model_storage.save(self._do_prepare_model())
        logger.info("Prepared model with uri: {}".format(self.storage_uri))
        return self.storage_uri

    def _do_prepare_model(self):
        raise NotImplementedError("_do_prepare_storage method not implemented")

    def deploy(self):
        if self.status() and not self.replace:
            raise RuntimeError("serving service {} already exists".format(self.service_name))

        if self.isvc is None:
            logger.info("Preparing model storage and InferenceService spec...")
            self.prepare_model()
            self.prepare_isvc()
        if self.isvc.metadata.annotations is None:
            self.isvc.metadata.annotations = {}
        # add a different annotation to force replace
        self.isvc.metadata.annotations[ANNOTATION_HSE_UUID] = str(uuid.uuid4())

        if isinstance(self.model_storage, MinIOModelStorage) and self.share_storage_creds:
            self.prepare_sa_secret()

        if self.status() is None:
            logger.info("Creating InferenceService {}...".format(self.service_name))
            self.created_isvc = self.kfserving_client.create(self.isvc, namespace=self.namespace)
        else:
            logger.info("Replacing InferenceService {}...".format(self.service_name))
            self.isvc.metadata.resource_version = None
            self.created_isvc = self.kfserving_client.replace(self.service_name, self.isvc,
                                                              namespace=self.namespace)
        logger.info("InferenceService: {} created. To check service readiness, "
                    "call this deployer's status(), wait() methods, or use "
                    "KFServing query APIs"
                    .format(self.service_name))
        return self.created_isvc

    def prepare_isvc(self):
        if self.isvc is None:
            self.isvc = kfserving.V1beta1InferenceService(
                api_version=kfserving.constants.KFSERVING_V1BETA1,
                kind=kfserving.constants.KFSERVING_KIND,
                metadata=client.V1ObjectMeta(name=self.service_name),
                spec=kfserving.V1beta1InferenceServiceSpec(
                    predictor=kfserving.V1beta1PredictorSpec()))
            self._do_prepare_predictor()
            if self.namespace:
                self.isvc.metadata.namespace = self.namespace
        logger.info("InferenceService spec ready")
        logger.debug(self.isvc)
        return self.isvc

    def _do_prepare_predictor(self):
        raise NotImplementedError("_do_prepare_predictor method not implemented")

    def destroy(self):
        if self.status() is not None:
            self.kfserving_client.delete(self.service_name, namespace=self.namespace)
            logger.info("InferenceService {} is deleted".format(self.service_name))
        return None

    def status(self):
        try:
            return self.kfserving_client.get(self.service_name, namespace=self.namespace)
        except RuntimeError as e:
            if "Reason: Not Found" in str(e):
                return None

    def wait(self, timeout=120):
        """Wait until the service becomes ready

        Internally calls KFServing API to retrieve the status

        :param timeout: seconds to wait
        :return: the InferenceService dict
        """
        return self.kfserving_client.get(self.service_name,
                                         namespace=self.namespace,
                                         watch=True,
                                         timeout_seconds=timeout)

    def prepare_sa_secret(self):
        secrets = client.CoreV1Api().list_namespaced_secret(self.namespace)
        secret_names = [secret.metadata.name for secret in secrets.items]
        annotations = {
            "serving.kubeflow.org/s3-endpoint": self.model_storage.endpoint,
            "serving.kubeflow.org/s3-usehttps": "1" if self.model_storage.secure else "0"
        }
        secret = client.V1Secret(metadata=client.V1ObjectMeta(name=MINIO_K8S_SECRET_NAME,
                                                              annotations=annotations),
                                 type="Opaque",
                                 string_data={
                                     'AWS_ACCESS_KEY_ID': self.model_storage.access_key,
                                     'AWS_SECRET_ACCESS_KEY': self.model_storage.secret_key
                                 })
        if MINIO_K8S_SECRET_NAME not in secret_names:
            client.CoreV1Api().create_namespaced_secret(self.namespace, secret)
        else:
            client.CoreV1Api().patch_namespaced_secret(MINIO_K8S_SECRET_NAME, self.namespace, secret)

        sa_name = self.isvc.spec.predictor.service_account_name \
            if (self.isvc and
                isinstance(self.isvc, kfserving.V1beta1InferenceService) and
                self.isvc.spec.predictor.service_account_name) \
            else "default"
        creds_utils.set_service_account(self.namespace,
                                        sa_name,
                                        MINIO_K8S_SECRET_NAME)
