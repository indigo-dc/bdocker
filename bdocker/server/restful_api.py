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

from flask import Flask
from flask import json, jsonify, request, abort
import sys

from bdocker.server import utils
from bdocker.common import utils as utils_common

sys.tracebacklimit = 0

app = Flask(__name__)
conf = utils_common.load_configuration()

credentials_module = utils.load_credentials_module(conf)
batch_module = utils.load_batch_module(conf)
docker_module = utils.load_docker_module(conf)

utils.set_error_handler(app)


@app.route('/credentials', methods=['PUT'])
def credentials():
    data = request.get_json()
    required = {'token','user_credentials'}
    utils.validate(data, required)
    token = data['token']
    user = data['user_credentials']
    results = credentials_module.authenticate(token, user)
    return utils.make_json_response(201, results)


@app.route('/pull', methods=['PUT'])
def pull():
    data = request.get_json()
    required = {'token','repo'}
    utils.validate(data, required)
    token = data['token']
    repo = data['repo']
    credentials_module.authorize(token)
    results = docker_module.pull_image(repo)
    credentials_module.add_container(token, results)
    return utils.make_json_response(201, results)


@app.route('/rm', methods=['DELETE'])
def delete():
    data = request.args
    required = {'token', 'container_id'}
    utils.validate(data, required)
    token = data['token']
    container_id = data['container_id']
    credentials_module.authorize_container(token,
                                           container_id)
    results = docker_module.delete_container(container_id)
    credentials_module.remove_container(token, container_id)
    return utils.make_json_response(204, results)


@app.route('/ps', methods=['GET'])
def list():
    data = request.args
    required = {'token'}
    utils.validate(data, required)
    token = data['token']
    containers = credentials_module.list_containers(token)
    results = docker_module.list_containers(containers)
    return utils.make_json_response(200, results)


@app.route('/logs', methods=['GET'])
def logs():
    data = request.args
    required = {'token'}
    utils.validate(data, required)
    token = data['token']
    container_id = data['container_id']
    credentials_module.authorize_container(token,
                                           container_id)
    results = docker_module.logs_container(container_id)
    return utils.make_json_response(200, results)


@app.route('/start', methods=['POST'])
def start():
    data = json.loads(request.data)
    required = {'token','container_id'}
    utils.validate(data, required)
    token = data['token']
    container_id = data['container_id']
    credentials_module.authorize_container(token,
                                           container_id)
    results = docker_module.start_container(container_id)
    return utils.make_json_response(201, results)


@app.route('/stop', methods=['POST'])
def stop():
    data = json.loads(request.data)
    required = {'token','container_id'}
    utils.validate(data, required)
    token = data['token']
    container_id = data['container_id']
    credentials_module.authorize_container(token,
                                           container_id)
    results = docker_module.stop_container(
        container_id)
    return utils.make_json_response(200, results)


@app.route('/run', methods=['POST'])
def run():
    data = json.loads(request.data)
    required = {'token','container_id', 'script'}
    utils.validate(data, required)
    token = data['token']
    container_id = data['container_id']
    script = data['script']
    credentials_module.authorize_container(token,
                                           container_id)
    results = docker_module.run_container(
        container_id,
        script)
    return utils.make_json_response(201, results)


@app.route('/accounting', methods=['GET'])
def accounting():
    data = request.args
    required = {'token'}
    utils.validate(data, required)
    token = data['token']
    # todo: study the implementation
    token_info = credentials_module.authorize(token)
    results = docker_module.accounting_container(token_info)
    return utils.make_json_response(200, results)


@app.route('/output', methods=['GET'])
def output():
    data = request.args
    required = {'token','container_id'}
    utils.validate(data, required)
    token = data['token']
    container_id = data['container_id']
    credentials_module.authorize_container(token,
                                           container_id)
    results = docker_module.output_task(container_id)
    return utils.make_json_response(200, results)


if __name__ == '__main__':
    app.run(host=conf['server']['host'],
            port=int(conf['server']['port']),
            debug=conf['server']['debug'])
