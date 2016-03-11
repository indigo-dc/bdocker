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

from bdocker.server import credentials
from bdocker.server import docker
from bdocker.server import utils

app = Flask(__name__)
credentials_module = credentials.UserController()
docker_module = docker.DockerController()

@app.route('/token')
def token():
    data = request.get_json()
    utils.validate(data, None)
    results = credentials_module.create_token()
    return jsonify(results)

@app.route('/pull')
def pull():
    data = request.get_json()
    utils.validate(data, None)
    results = docker_module.pull_container()
    return jsonify(results)

@app.route('/delete')
def delete():
    return "Hello, World!"

@app.route('/list')
def list():
    return "Hello, World!"

@app.route('/logs')
def logs():
    return "Hello, World!"

@app.route('/start')
def start():
    return "Hello, World!"

@app.route('/stop')
def stop():
    return "Hello, World!"

@app.route('/run')
def run():
    return "Hello, World!"

@app.route('/accounting')
def accounting():
    return "Hello, World!"


if __name__ == '__main__':
    app.run(host='127.0.0.33',
            port=5000, debug=True)
    #todo(jorgesece): configure from file