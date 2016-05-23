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
import ConfigParser
import os
import pwd
import yaml

from bdocker.common import exceptions


def read_yaml_file(path):
    f = open(path, 'r')
    data = f.read()
    f.close()
    return yaml.load(data)


def write_yaml_file(path, data):
    with open(path,'w') as my_file:
        data_yaml = yaml.safe_dump(data, None, encoding='utf-8', allow_unicode=True)
        my_file.write(data_yaml)
        my_file.flush()
        my_file.close()


default_conf_file = ("/root/" +
                     "configure_bdocker.cfg"
                     )


def validate_config(conf):
    section_keys = {'server', 'batch', 'credentials', 'dockerAPI'}
    server_keys = {'host', 'port', 'environ'}
    environ_options = {'public', 'debug', 'private'}
    batch_keys = {'system'}
    credentials_keys = {'token_store', 'token_client_file'}
    dockers_keys = {'base_url'}
    for key in section_keys:
        if key not in conf:
            raise exceptions.ParseException(key)
    for key in server_keys:
        if key not in conf['server']:
            raise exceptions.ParseException('"server":' + key)

    if conf['server']['environ'] not in environ_options:
        raise exceptions.ParseException(
            '"environ" has wrong value.'
        )
    for key in batch_keys:
        if key not in conf['batch']:
            raise exceptions.ParseException(
                'batch: %s missed in configuration file' % key)
    for key in credentials_keys:
        if key not in conf['credentials']:
            raise exceptions.ParseException(
                'credentials: %s missed in'
                ' configuration file' % key)
    for key in dockers_keys:
        if key not in conf['dockerAPI']:
            raise exceptions.ParseException(
                'dockerAPI: %s missed in '
                'configuration file' % key)


def load_configuration_from_file(path=None):

    config = ConfigParser.SafeConfigParser()
    if not path:
        path = os.getenv(
            'BDOCKER_CONF_FILE',
            default_conf_file)
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
            "Parameter %s"
            % e.message)
    except BaseException as e:
        raise exceptions.ConfigurationException(
            "Error reading configuration file:"
            " %s" % path)
    return conf


def check_user_credentials(user_info):
    info = pwd.getpwuid(user_info['uid'])
    if user_info['gid'] == info.pw_gid:
        home_dir = os.path.realpath(info.pw_dir)
        if user_info['home'] == home_dir:
            return True
    raise exceptions.UserCredentialsException(
        "Invalid user in the server"
    )


def validate_directory(dir_request, dir_user):
    real_path = os.path.realpath(dir_request)
    prefix = os.path.commonprefix([real_path, dir_user])
    if prefix != dir_user:
        raise exceptions.UserCredentialsException(
            "User does not have permissons for %s"
            % real_path
        )


def read_user_credentials(file_path):
    # TODO(jorgesece): add to the commom package
    input = open(file_path,'r')
    token = input.read().rstrip('\n')
    input.close()
    return token