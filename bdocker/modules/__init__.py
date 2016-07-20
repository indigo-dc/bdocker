# -*- coding: utf-8 -*-

# Copyright 2015 LIP - INDIGO-DataCloud
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

from bdocker import exceptions
from bdocker.modules import batch
from bdocker.modules import credentials
from bdocker.modules import docker_helper


def load_credentials_module(conf):
    if 'credentials' not in conf:
        raise exceptions.ConfigurationException("Credentials system is not defined")
    try:
        credentials_module = conf['credentials']["controller"]
        credentials_class = getattr(credentials, credentials_module)
        path = conf["credentials"]['token_store']
        return credentials_class(path)
    except BaseException:
        raise exceptions.ConfigurationException("Credentials is not supported")


def load_batch_module(conf):
    if 'batch' not in conf:
        raise exceptions.ConfigurationException("Batch system is not defined")
    try:
        batch_module = conf['batch']["controller"]
        batch_class = getattr(batch, batch_module)
        if conf["resource"]["role"] == "working":
            return batch_class(conf['batch'], conf['accounting_server'])
        else:
            return batch_class(conf['batch'])
    except BaseException:
        raise exceptions.ConfigurationException("Batch is not supported")


def load_docker_module(conf):
    return docker_helper.DockerController(
        conf['dockerAPI']['base_url']
    )
