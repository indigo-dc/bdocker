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
import webob
from flask import jsonify

from bdocker.common import exceptions


default_conf_file = ("/root/" +
                     "configure_bdocker.cfg"
                     )


def load_configuration(path=None):

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


def eval_bool(s):
    if s:
        if s == 'True':
            return True
        else:
            return False


def validate(fields, mandatory_keys):
    try:
        for key in mandatory_keys:
            if (key not in fields):
                raise webob.exc.HTTPBadRequest(
                    "The %s field is mandatory."
                    "" % key)
    except Exception as e:
        raise exceptions.ParseException("Validation of required values")
    return True


def make_json_response(status_code, description):
    return jsonify({
        'status_code': status_code,
        'results': description
    }), status_code


def error_json_handler(exception):
    ex = exceptions.manage_http_exception(exception.code, exception.message)
    response = make_json_response(ex.code, ex.message)
    return response


def set_error_handler(app):
    for code in exceptions.default_exceptions.iterkeys():
        app.error_handler_spec[None][code] = error_json_handler


def manage_exceptions(e):
    if isinstance(e, exceptions.UserCredentialsException):
        return make_json_response(401, e.message)
    if isinstance(e, exceptions.DockerException):
        return make_json_response(e.code, e.message)
    if isinstance(e, exceptions.ParseException):
        return make_json_response(400, e.message)
    return make_json_response(500, e.message)


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
