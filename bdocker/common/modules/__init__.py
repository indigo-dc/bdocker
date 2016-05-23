# -*- coding: utf-8 -*-

# Copyright 2016 LIP - Lisbon
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

from bdocker.common import exceptions
from bdocker.common.modules import batch, credentials, docker_helper


def load_credentials_module(conf):
    path = conf["credentials"]['token_store']
    return credentials.UserController(path)


def load_batch_module(conf):
    if 'batch' not in conf:
        raise exceptions.ConfigurationException("Batch system is not defined")
    if conf['batch']["system"] == 'SGE':
        return batch.SGEController()
    exceptions.ConfigurationException("Batch is not supported")


def load_docker_module(conf):
    return docker_helper.DockerController(
        conf['dockerAPI']['base_url']
    )