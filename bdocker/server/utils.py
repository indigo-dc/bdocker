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
import webob
from flask import jsonify

from bdocker.common import exceptions
from bdocker.server.modules import batch, docker_helper
from bdocker.server.modules import credentials


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
            "Parameter %s missed in configuration file."
            % e.message)
    except BaseException as e:
        raise exceptions.ConfigurationException(
            "Error reading configuration file.")
    return conf


def validate_config(conf):
    section_keys = {'server', 'batch', 'credentials', 'dockerAPI'}
    server_keys = {'host','port','environ'}
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
