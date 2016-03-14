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

from bdocker.server import utils

app = Flask(__name__)
conf = utils.load_configuration()

credentials_module = utils.load_credentials_module(conf)
batch_module = utils.load_batch_module(conf)
docker_module = utils.load_docker_module(conf)


@app.route('/token')
def token():
    data = request.get_json()
    utils.validate(data, None) # todo(jorgesece): define userdata
    results = credentials_module.authenticate(data)
    return jsonify(results)


@app.route('/pull')
def pull():
    data = request.get_json()
    utils.validate(data, None)
    results = docker_module.pull_container()
    return jsonify(results)


@app.route('/delete')
def delete():
    data = request.get_json()
    utils.validate(data, None)
    results = docker_module.delete_container()
    return jsonify(results)


@app.route('/ps')
def list():
    data = request.get_json()
    utils.validate(data, None)
    results = docker_module.list_container()
    return jsonify(results)


@app.route('/logs')
def logs():
    data = request.get_json()
    utils.validate(data, None)
    results = docker_module.logs_container()
    return jsonify(results)


@app.route('/start')
def start():
    data = request.get_json()
    utils.validate(data, None)
    results = docker_module.start_container()
    return jsonify(results)


@app.route('/stop')
def stop():
    data = request.get_json()
    utils.validate(data, None)
    results = docker_module.stop_container()
    return jsonify(results)


@app.route('/run')
def run():
    data = request.get_json()
    utils.validate(data, None)
    results = docker_module.run_container()
    return jsonify(results)


@app.route('/accounting')
def accounting():
    data = request.get_json()
    utils.validate(data, None)
    results = docker_module.accounting_user()
    return jsonify(results)

@app.route('/output')
def output():
    data = request.get_json()
    utils.validate(data, None)
    results = docker_module.output_task()
    return jsonify(results)


if __name__ == '__main__':
    app.run(host=conf['host'],
            port=conf['port'],
            debug=conf['debug'])
