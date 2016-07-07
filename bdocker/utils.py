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

try:
    import ConfigParser as cfg
except Exception:
    import configparser as cfg
import io
import os
import pwd
import re
import tarfile
import uuid

import yaml

from bdocker import exceptions


WORKING_NODE = 'working'


def read_yaml_file(path):
    f = open(path, 'r')
    data = f.read()
    f.close()
    return yaml.load(data)


def write_yaml_file(path, data):
    with open(path, 'w') as my_file:
        data_yaml = yaml.safe_dump(data, None,
                                   encoding='utf-8',
                                   allow_unicode=True)
        my_file.write(data_yaml)
        my_file.flush()
        my_file.close()


def update_yaml_file(path, data):
    with open(path, 'r+') as my_file:
        current_data = my_file.read()
        plain_data = yaml.load(current_data)
        plain_data.update(data)
        data_yaml = yaml.safe_dump(plain_data, None,
                                   encoding='utf-8',
                                   allow_unicode=True
                                   )
        my_file.seek(0)
        my_file.write(data_yaml)
        my_file.truncate()
        my_file.close()


def delete_file(path):
    os.remove(path)


default_conf_file = "/etc/configure_bdocker.cfg"


def validate_config(conf):
    section_keys = {'resource', 'server', 'batch',
                    'credentials'}
    server_keys = {'host', 'port', 'environ'}
    acc_server_keys = {'host', 'port'}
    resource_options = {'working', 'accounting'}
    environ_options = {'public', 'debug', 'private'}
    batch_keys = {'system'}
    credentials_keys = {'token_store'}
    dockers_keys = {'base_url'}
    for key in section_keys:
        if key not in conf:
            raise exceptions.ParseException(key)
    # RESOURCE
    if conf['resource']["role"] not in resource_options:
        raise exceptions.ParseException(
            '"resource" has wrong value.'
        )
    role = conf['resource']["role"]
    # SERVER API
    server = conf['server']
    for key in server_keys:
        if key not in server:
            raise exceptions.ParseException(
                '"Working node server":' + key
            )
    if server['environ'] not in environ_options:
        raise exceptions.ParseException(
            '"environ" has wrong value in the server.'
        )

    # BATCH MODULE
    for key in batch_keys:
        if key not in conf['batch']:
            raise exceptions.ParseException(
                'batch: %s missed in configuration file'
                % key)
    # CREDENTIAL MODULE
    for key in credentials_keys:
        if key not in conf['credentials']:
            raise exceptions.ParseException(
                'credentials: %s missed in'
                ' configuration file' % key)

    # WORKING NODE CONFIGURATION
    if WORKING_NODE == role:
        # ACCOUNTING SERVER
        acc_server = conf['accounting_server']
        for key in acc_server_keys:
            if key not in acc_server:
                raise exceptions.ParseException(
                    '"Accounting server configuration": %s'
                    % key
                )
        # DOCKER MODULE
        docker_info = conf['dockerAPI']
        for key in dockers_keys:
            if key not in docker_info:
                raise exceptions.ParseException(
                    'dockerAPI: %s missed in '
                    'configuration file' % key)


def load_configuration_from_file(path=None):

    config = cfg.SafeConfigParser()
    if not path:
        path = os.getenv(
            'BDOCKER_CONF_FILE',
            default_conf_file)
    try:
        with open(path) as f:
            config.readfp(f)
    except IOError:
        raise exceptions.UserCredentialsException(
            "Error reading configuration file: %s"
            % path
        )
    try:
        conf = {
            'resource': dict(config.items("resource")),
            'server': dict(config.items("server")),
            'batch': dict(config.items("batch")),
            'credentials': dict(config.items("credentials")),
        }
        if WORKING_NODE == conf["resource"]["role"]:
            conf.update(
                {
                    'accounting_server':
                        dict(config.items("accounting_server")),
                    'dockerAPI': dict(config.items("dockerAPI"))
                }
            )
        validate_config(conf)
    except exceptions.ParseException as e:
        raise exceptions.ConfigurationException(
            '"%s" not found'
            % e.message)
    except BaseException as e:
        raise exceptions.ConfigurationException(
            message=None, exc=e)
    return conf


def load_sge_job_configuration(path):
    config = cfg.SafeConfigParser()
    f = None
    try:
        with open(path, 'r') as f:
            string = '[root]\n' + f.read()
            ini_fp = io.BytesIO(string)
            config.readfp(ini_fp)
    except IOError:
        raise exceptions.UserCredentialsException(
            "Error reading job configuration file: %s"
            % path
        )
    finally:
        if f:
            f.close()
    config_dict = dict(config.items("root"))
    return config_dict


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
    user_real_path = os.path.realpath(dir_user)
    prefix = os.path.commonprefix([real_path, user_real_path])
    if prefix != dir_user:
        raise exceptions.UserCredentialsException(
            "User does not have permissons for %s"
            % real_path
        )


def read_user_credentials(file_path):
    return read_file(file_path)


def read_file(file_path):
    stream_read = open(file_path, 'r')
    token = stream_read.read().rstrip('\n')
    stream_read.close()
    return token


def find_line(file_path, search_str):
    found = None
    stream_read = open(file_path, 'r')
    line = stream_read.readline()
    # Loop until EOF
    while line != '':
        # Search for string in line
        index = re.findall(search_str, line)
        if index > 0:
            return line
        # Read next line
        line = stream_read.readline()
    # Close the files
    stream_read.close()
    return found


def add_to_file(file_path, data):
    with open(file_path, 'a') as file_obj:
        file_obj.write(data)
    file_obj.close()
    return True


def write_tar_raw_data_stream(path, stream, uid, gid):
    strema_io = io.StringIO(stream)
    my_tar = tarfile.TarFile(fileobj=strema_io)
    my_tar.extractall(path=path)
    change_owner_dir(path, uid, gid)


def read_tar_raw_data_stream(path):
    file_name = "/tmp/%s.tar" % uuid.uuid4().hex
    tar_stream = tarfile.TarFile(file_name, mode="w")
    arcname = os.path.basename(path)
    tar_stream.add(path, arcname=arcname)
    tar_stream.close()
    io_stream = io.FileIO(file_name, 'r')
    return io_stream


def change_owner_dir(path, uid, gid):
    for root, dirs, files in os.walk(path):
        for momo in dirs:
            os.chown(os.path.join(root, momo), uid, gid)
        for momo in files:
            os.chown(os.path.join(root, momo), uid, gid)
