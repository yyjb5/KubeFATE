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

from .converters import get_converter
from .deployers import get_deployer
from .trained_model import get_trained_model


class HSEngine(object):
    def __init__(self,
                 service_name,
                 version="1.0",
                 converter_kwargs=None,
                 deployer_kwargs=None,
                 **kwargs):
        """
        :param service_name: the service name
        :param version: the service version, default to "1.0"
        :param converter_kwargs: a dict of keyword arguments that will be used to infer
                                 and initialize the converter. See the doc of get_converter
                                 and subclasses of ConverterBase for supported arguments.
        :param deployer_kwargs: a dict of keyword arguments that will be used to infer
                                the deployer type and initialize it. See the doc of
                                get_deployer() and subclasses of the ConverterBase class
                                for supported arguments.
        :param kwargs: keyword arguments to describe the original trained model. See the
                       doc of the derived TrainedModel class for supported arguments.
        """
        if converter_kwargs is None:
            converter_kwargs = {}
        if deployer_kwargs is None:
            deployer_kwargs = {}
        self.service_name = service_name
        self.version = version
        self.converter_kwargs = converter_kwargs
        self.deployer_kwargs = deployer_kwargs
        self.converter = None
        self.deployer = None
        self.trained_model = get_trained_model(**kwargs)
        self.converted_model = None
        pass

    def infer_converter(self):
        self.converter = get_converter(self.trained_model, **self.converter_kwargs)
        return self.converter

    def infer_deployer(self):
        if not self.converted_model:
            if not self.converter:
                self.infer_converter()
            self.converted_model = self.converter.convert()
        self.deployer = get_deployer(self.service_name,
                                     self.version,
                                     self.converted_model,
                                     **self.deployer_kwargs)
        return self.deployer

    def run(self):
        """Starts the engine

        May auto-create converter and deployer
        :returns: the deployed service
        :rtype: depends on the deployer instance
        """
        if not self.converter:
            self.infer_converter()
        self.converted_model = self.converter.convert()

        if not self.deployer:
            self.infer_deployer()
        return self.deployer.deploy()
