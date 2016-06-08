# -*- coding: utf-8 -*-

# Copyright 2015 LIP - INDIGODataCLOUD
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
from flask import json, request
import logging

#from bdocker.common import modules as modules_common
from bdocker.server import controller
from bdocker.common import utils as utils_common
from bdocker.server import utils as utils_server

conf = utils_common.load_configuration_from_file()
server_controller = controller.ServerController(conf)
#credentials_module = modules_common.load_credentials_module(conf)
#batch_module = modules_common.load_batch_module(conf)
#docker_module = modules_common.load_docker_module(conf)

app = Flask(__name__)

LOG = logging.getLogger(__name__)

utils_server.set_error_handler(app)


@app.route('/credentials', methods=['POST'])
def credentials():
    """
    DEPRECATED
    :return:
    """
    data = request.get_json()
    required = {'admin_token', 'user_credentials'}
    utils_server.validate(data, required)
    user_token = server_controller.credentials(data)
    return utils_server.make_json_response(
        201, user_token
    )


@app.route('/batchconf', methods=['PUT'])
def batch_conf():
    """
    DEPRECATED
    :return:
    """
    data = request.get_json()
    required = {'admin_token', 'token'}
    utils_server.validate(data, required)
    server_controller.batch_configuration()
    return utils_server.make_json_response(
        201, ["Batch system configured"]
    )


@app.route('/configuration', methods=['POST'])
def configuration():
    """Configure bdocker user environment.
      It creates the token and configure the batch
      system.

    :return: user_token
    """
    data = request.get_json()
    required = {'admin_token', 'user_credentials'}
    utils_server.validate(data, required)
    user_token = server_controller.configuration(data)
    return utils_server.make_json_response(
        201, user_token
    )


@app.route('/clean', methods=['DELETE'])
def clean():
    """Clean bdocker user environment.
      Delete the remaining containers and the token.
      In addition, it cleans the batch environment.

    :return: Request 204 with user_token
    """
    data = request.args
    required = {'admin_token', 'token'}
    utils_server.validate(data, required)
    result = server_controller.clean(data)

    return utils_server.make_json_response(204, [result])


@app.route('/pull', methods=['POST'])
def pull():
    """Pull request.
    Download a docker image from a repository

    :return: Request 201 with output
    """
    data = request.get_json()
    required = {'token','source'}
    utils_server.validate(data, required)
    result = server_controller.pull(data)
    return utils_server.make_json_response(201, result)


@app.route('/run', methods=['PUT'])
def run():
    """Execute command in container.

    :return: Request 201 with results
    """
    data = json.loads(request.data)
    required = {'token','image_id', 'script'}
    utils_server.validate(data, required)
    results = server_controller.run(data)
    return utils_server.make_json_response(201, results)


@app.route('/ps', methods=['GET'])
def list_containers():
    """List containers.

    :return: Request 200 with results
    """
    data = request.args
    required = {'token'}
    utils_server.validate(data, required)
    results = server_controller.list_containers(data)
    return utils_server.make_json_response(200, results)


@app.route('/inspect', methods=['GET'])
def show():
    """Show container information.

    :return: Request 200 with results
    """
    data = request.args
    required = {'token'}
    utils_server.validate(data, required)
    results = server_controller.show(data)
    return utils_server.make_json_response(200, results)


@app.route('/logs', methods=['GET'])
def logs():
    """Log from a contaniner.

    :return: Request 200 with results
    """
    data = request.args
    required = {'token', "container_id"}
    utils_server.validate(data, required)
    results = server_controller.logs(data)
    return utils_server.make_json_response(200, results)


@app.route('/rm', methods=['PUT'])
def delete():
    """Delete a container.

    :return: Request 200 with results
    """
    data = json.loads(request.data)
    required = {'token', 'container_id'}
    utils_server.validate(data, required)
    docker_out = server_controller.delete(data)
    return utils_server.make_json_response(200, docker_out)


########################
### UN IMPLEMENTED ####
######################


@app.route('/stop', methods=['POST'])
def stop():
    data = json.loads(request.data)
    required = {'token','container_id'}
    utils_server.validate(data, required)
    results = server_controller.delete_container(data)
    return utils_server.make_json_response(200, results)


@app.route('/accounting', methods=['GET'])
def accounting():
    data = request.args
    required = {'token'}
    utils_server.validate(data, required)
    results = server_controller.accounting(data)
    return utils_server.make_json_response(200, results)


@app.route('/output', methods=['GET'])
def output():
    data = request.args
    required = {'token','container_id'}
    utils_server.validate(data, required)
    results = server_controller.output(data)
    return utils_server.make_json_response(200, results)

#####  UNIMPLEMETED  ######
###########################

if __name__ == '__main__':
    environ = conf['server']['environ']
    port = int(conf['server']['port'])
    host = conf['server']['host']
    debug = False
    if environ == 'public':
        host = '0.0.0.0'
    elif environ == 'debug':
        debug = True
    app.run(host=host,
                port=port,
                debug=debug)
