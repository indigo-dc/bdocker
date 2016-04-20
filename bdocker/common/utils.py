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
import yaml
import ConfigParser

from bdocker.common import exceptions

default_conf_file = ("/home/jorge/Dropbox" +
                     "/INDIGO_DOCKER/bdocker/" +
                     "bdocker/common/"
                     "configure_bdocker.cfg"
                     )


def load_configuration(path=None):

    config = ConfigParser.SafeConfigParser()
    if not path:
        path = default_conf_file
    try:
        with open(path) as f:
            config.readfp(f)
    except IOError:
        raise exceptions.UserCredentialsException(
            "No administration permission"
        )
    try:
        conf = {
            'server': dict(config.items("server")),
            'batch': dict(config.items("batch")),
            'credentials': dict(config.items("credentials")),
            'dockerAPI': dict(config.items("dockerAPI"))
        }
        validate_config(conf)
    except exceptions.ParseException as e:
        raise exceptions.ConfigurationException(
            "Parameter %s missed in configuration file."
            % e.message)
    except BaseException as e:
        raise exceptions.ConfigurationException(
            "Error reading configuration file.")
    return conf


def validate_config(conf):
    section_keys = {'server', 'batch', 'credentials', 'dockerAPI'}
    server_keys = {'host','port','debug'}
    batch_keys = {'system'}
    credentials_keys = {'token_store', 'token_client_file'}
    dockers_keys = {'base_url'}
    for key in section_keys:
        if key not in conf:
            raise exceptions.ParseException(key)
    for key in server_keys:
        if key not in conf['server']:
            raise exceptions.ParseException('server:' + key)
    for key in batch_keys:
        if key not in conf['batch']:
            raise exceptions.ParseException('batch:' +key)
    for key in credentials_keys:
        if key not in conf['credentials']:
            raise exceptions.ParseException('credentials:' + key)
    for key in dockers_keys:
        if key not in conf['dockerAPI']:
            raise exceptions.ParseException('dockerAPI:' + key)


def read_yaml_file(path):
    f = open(path, 'r')
    data = f.read()
    f.close()
    return yaml.load(data)


def write_yaml_file(path, data):
    f = open(path, 'w')
    f.write(yaml.dump(data, default_flow_style=False))
    f.close()