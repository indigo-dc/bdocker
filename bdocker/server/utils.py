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

import webob
from flask import jsonify

from bdocker import exceptions
from bdocker.server.modules import batch
from bdocker.server.modules import credentials
from bdocker.server import docker


def validate(dict, mandatory_keys):
    try:
        for key in mandatory_keys:
            if (key not in dict):
                raise webob.exc.HTTPBadRequest(
                    "The {0} field is mandatory."
                    "".format(key))
    except Exception as e:
        raise exceptions.ParseException("Validation of required values")
    return True


def load_configuration():

    conf = {}
    server = {'host': '127.0.0.33',
              'port': 5000,
              'debug': False
              }
    conf['server'] = server
    conf['batch'] = 'SGE'

    # todo(jorgesece): read from file
    # conf = ConfigParser.ConfigParser()
    # config.read('example.cfg')
    return conf


def load_credentials_module(conf):
    path = '/home/jorge/toke_store.yml'
    return credentials.UserController(path)


def load_batch_module(conf):
    if 'batch' not in conf:
        raise exceptions.ConfigurationException("Batch system is not defined")
    if conf['batch'] == 'SGE':
        return batch.SGEController()
    exceptions.ConfigurationException("Batch is not supported")


def load_docker_module(conf):
    return docker.DockerController()



def make_json_response(status_code, description):
    return jsonify({
        'status_code': status_code,
        'description': description
    })


def error_json_handler(exception):
    ex = exceptions.manage_http_exception(exception.code, exception.message)
    response = make_json_response(ex.code, ex.message)
    return response


def set_error_handler(app):
    for code in exceptions.default_exceptions.iterkeys():
        app.error_handler_spec[None][code] = error_json_handler

