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
from flask import jsonify, request, abort
import sys

from bdocker.server import utils

sys.tracebacklimit=0

app = Flask(__name__)
conf = utils.load_configuration()

credentials_module = utils.load_credentials_module(conf)
batch_module = utils.load_batch_module(conf)
docker_module = utils.load_docker_module(conf)

utils.set_error_handler(app)


@app.route('/token', methods=['PUT'])
def token():
    data = request.get_json()
    required = {}
    utils.validate(data, required) # todo(jorgesece): define userdata
    data = {'uid': 'uuuuuuuuuuiiiidddddd', 'guid': 'gggggggggguuuiiidd'}
    results = credentials_module.authenticate(data)
    return utils.make_json_response(200, results)


@app.route('/pull', methods=['PUT'])
def pull():
    data = request.get_json()
    required = {}
    utils.validate(data, required)
    results = docker_module.pull_container()
    return utils.make_json_response(201,results)


@app.route('/delete', methods=['DELETE'])
def delete():
    data = request.get_json()
    required = {}
    utils.validate(data, required)
    results = docker_module.delete_container()
    return utils.make_json_response(204,results)


@app.route('/ps', methods=['GET'])
def list():
    data = request.get_json()
    required = {}
    utils.validate(data, required)
    results = docker_module.list_container()
    return utils.make_json_response(200,results)


@app.route('/logs', methods=['GET'])
def logs():
    data = request.get_json()
    required = {}
    utils.validate(data, required)
    results = docker_module.logs_container()
    return utils.make_json_response(200,results)


@app.route('/start', methods=['POST'])
def start():
    data = request.get_json()
    required = {}
    utils.validate(data, required)
    results = docker_module.start_container()
    return utils.make_json_response(201,results)


@app.route('/stop', methods=['POST'])
def stop():
    data = request.get_json()
    required = {}
    utils.validate(data, required)
    results = docker_module.stop_container()
    return utils.make_json_response(200,results)


@app.route('/run', methods=['POST'])
def run():
    data = request.get_json()
    required = {}
    utils.validate(data, required)
    results = docker_module.run_container()
    return utils.make_json_response(201,results)


@app.route('/accounting', methods=['GET'])
def accounting():
    data = request.get_json()
    required = {}
    utils.validate(data, required)
    results = docker_module.accounting_user()
    return utils.make_json_response(200,results)


@app.route('/output', methods=['GET'])
def output():
    data = request.get_json()
    required = {}
    utils.validate(data, required)
    results = docker_module.output_task()
    return utils.make_json_response(200,results)


if __name__ == '__main__':
    app.run(host=conf['server']['host'],
            port=conf['server']['port'],
            debug=conf['server']['debug'])
