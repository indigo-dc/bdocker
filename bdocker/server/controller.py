# -*- coding: utf-8 -*-

# Copyright 2015 LIP - Lisbon
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import json

from bdocker.server import utils


class ServerController(object):

    def __init__(self, credentials_module,
                 docker_module,
                 batch_module=None):
        self.credentials_module = credentials_module
        self.docker_module = docker_module

    def run(self, data):

        token = data['token']
        image_id = data['image_id']
        script = data['script']
        detach = data.get('detach', False)
        host_dir = data.get('host_dir', None)
        docker_dir = data.get('docker_dir', None)
        working_dir = data.get('working_dir', None)
        # TODO(jorgesece): control image private
        # credentials_module.authorize_image(
        #     token,
        #     image_id
        # )
        if host_dir:
            self.credentials_module.authorize_directory(token, host_dir)
        container_id = self.docker_module.run_container(
            image_id,
            detach,
            script,
            host_dir=host_dir,
            docker_dir=docker_dir,
            working_dir=working_dir
        )
        self.credentials_module.add_container(token, container_id)
        self.docker_module.start_container(container_id)
        if not detach:
            results = self.docker_module.logs_container(container_id)
        else:
            results = container_id
        return  results
