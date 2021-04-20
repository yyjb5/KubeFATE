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

import json
import logging
import os
import tempfile
import zipfile

from flow_sdk.client import FlowClient


logger = logging.getLogger(__name__)

ENV_FATE_FLOW_HOST_KEY = "FATE_FLOW_HOST"
ENV_FATE_FLOW_PORT_KEY = "FATE_FLOW_PORT"

DEFAULT_FATE_FLOW_HOST = "fateflow"
DEFAULT_FATE_FLOW_PORT = 9380


class FATEFlowClient(object):
    """A client to the fate flow server

    By default FATE_FLOW_HOST and FATE_FLOW_PORT environment
    variables will be used to connect to fate flow server, unless
    specified by the caller
    """

    def __init__(self,
                 fate_flow_host=None,
                 fate_flow_port=None,
                 api_version="v1"):
        """
        :param fate_flow_host: fate flow server host address, defaults to None
        :type fate_flow_host: str, optional
        :param fate_flow_port: fate flow server port, defaults to None
        :type fate_flow_port: int, optional
        :param api_version: api version, defaults to "v1"
        :type api_version: str, optional
        """
        if not fate_flow_host:
            fate_flow_host = os.getenv(ENV_FATE_FLOW_HOST_KEY, DEFAULT_FATE_FLOW_HOST)
            name_list = fate_flow_host.split(":")
            fate_flow_host = name_list[0]
            if len(name_list) > 1:
                fate_flow_port = name_list[1]
        if not fate_flow_port:
            fate_flow_port = os.getenv(ENV_FATE_FLOW_PORT_KEY, DEFAULT_FATE_FLOW_PORT)
        fate_flow_port = int(fate_flow_port)
        logger.debug("host: {}, port: {}, api_version: {}"
                     .format(fate_flow_host, fate_flow_port, api_version))
        self.flow_client = FlowClient(fate_flow_host, fate_flow_port, api_version)

    def fetch_fate_model(self,
                         model_version,
                         role="guest",
                         party_id="",
                         model_id=""):
        """Download trained model from a running FATE server

        :param model_version: model version id recorded in fate flow
        :type model_version: str
        :param role: role of the party, defaults to "guest"
        :type role: str, optional
        :param party_id: party id of the model, defaults to ""
        :type party_id: str, optional
        :param model_id: id of the model, defaults to ""
        :type model_id: str, optional
        :returns: a local folder path to the downloaded model
        :rtype: str
        """
        client = self.flow_client
        if not model_id or not party_id:
            logger.debug("Query model info with role: {}, version: {}".format(role, model_version))
            query_result = client.model.get_model_info(model_version=model_version, role=role)
            if query_result['retcode'] != 0:
                raise RuntimeError("error querying fate model: {}".format(query_result['retmsg']))
            query_result = query_result['data'][0]
            model_id = query_result['f_model_id']
            party_id = query_result['f_party_id']

        logger.info("Downloading FATE model with role: {}, party_id: {}, model_id: {}, model_version: {}"
                    .format(role, party_id, model_id, model_version))
        temp_dir = tempfile.mkdtemp()
        export_config = {
            "role": role,
            "party_id": int(party_id),
            "model_id": model_id,
            "model_version": model_version,
            "output_path": temp_dir
        }
        conf_file = os.path.join(temp_dir, "export_model_conf.json")
        with open(conf_file, "w") as f:
            json.dump(export_config, f)

        export_result = client.model.export_model(conf_file)
        if export_result['retcode'] != 0:
            raise RuntimeError("error exporting fate model: {}".format(export_result['retmsg']))

        file_path = export_result['file']
        with zipfile.ZipFile(file_path, 'r') as archive:
            archive.extractall(temp_dir)
        logger.info("FATE model is saved to: {}".format(temp_dir))
        return temp_dir
