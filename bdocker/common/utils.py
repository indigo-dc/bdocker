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


def load_configuration():

    conf = {}
    server = {'host': '127.0.0.33',
              'port': 5000,
              'debug': False
              }
    conf['server'] = server
    conf['batch'] = 'SGE'
    conf['token_store'] = '/home/jorge/Dropbox/INDIGO_DOCKER/bdocker/bdocker/common/token_store.yml'
    conf["token_client_file"] = ".bdocker_token"
    # todo(jorgesece): read from file and validate fields
    # conf = ConfigParser.ConfigParser()
    # config.read('example.cfg')
    return conf


def read_yaml_file(path):
    with open(path, 'r') as f:
        data = f.read()
        f.close()
        return yaml.load(data)
    return None


def write_yaml_file(path, data):
    with open(path, 'w') as f:
        f.write(yaml.dump(data, default_flow_style=False))
        f.close()