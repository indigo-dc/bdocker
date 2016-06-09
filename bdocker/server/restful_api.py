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

from bdocker.server import controller
from bdocker.server import utils as utils_server
from bdocker.common import utils as utils_common

conf = utils_common.load_configuration_from_file()
server_controller = controller.ServerController(conf)

app = Flask(__name__)

LOG = logging.getLogger(__name__)

utils_server.set_error_handler(app)


@app.route('/credentials', methods=['POST'])
def credentials():
    """ Create user token environment
    DEPRECATED. Included in clean
    :return:
        """
    data = request.get_json()
    try:
        user_token = server_controller.credentials(data)
    except Exception as e:
        return utils_server.manage_exceptions(e)
    return utils_server.make_json_response(
        201, user_token
    )


@app.route('/batchconf', methods=['PUT'])
def batch_conf():
    """ Config batch system environment
    DEPRECATED. Included in clean
    :return:
    """
    data = request.get_json()
    try:
        server_controller.batch_configuration(data)
    except Exception as e:
        return utils_server.manage_exceptions(e)
    return utils_server.make_json_response(
        201, ["Batch system configured"]
    )

@app.route('/batchclean', methods=['DELETE'])
def batch_clean():
    """ Clean batch system environment
    DEPRECATED. Included in clean
    :return:
    """
    data = request.args
    try:
        server_controller.batch_clean(data)
    except Exception as e:
        return utils_server.manage_exceptions(e)
    return utils_server.make_json_response(204, [])


@app.route('/configuration', methods=['POST'])
def configuration():
    """Configure bdocker user environment.
      It creates the token and configure the batch
      system.

    :return: user_token
    """
    data = request.get_json()
    try:
        user_token = server_controller.configuration(data)
    except Exception as e:
        return utils_server.manage_exceptions(e)
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
    try:
        result = server_controller.clean(data)
    except Exception as e:
        return utils_server.manage_exceptions(e)
    return utils_server.make_json_response(204, [result])


@app.route('/pull', methods=['POST'])
def pull():
    """Pull request.
    Download a docker image from a repository

    :return: Request 201 with output
    """
    data = request.get_json()
    try:
        result = server_controller.pull(data)
    except Exception as e:
        return utils_server.manage_exceptions(e)
    return utils_server.make_json_response(201, result)


@app.route('/run', methods=['PUT'])
def run():
    """Execute command in container.

    :return: Request 201 with results
    """
    data = json.loads(request.data)
    try:
        results = server_controller.run(data)
    except Exception as e:
        return utils_server.manage_exceptions(e)
    return utils_server.make_json_response(201, results)


@app.route('/ps', methods=['GET'])
def list_containers():
    """List containers.

    :return: Request 200 with results
    """
    data = request.args
    try:
        results = server_controller.list_containers(data)
    except Exception as e:
        return utils_server.manage_exceptions(e)
    return utils_server.make_json_response(200, results)


@app.route('/inspect', methods=['GET'])
def show():
    """Show container information.

    :return: Request 200 with results
    """
    data = request.args
    try:
        results = server_controller.show(data)
    except Exception as e:
        return utils_server.manage_exceptions(e)
    return utils_server.make_json_response(200, results)


@app.route('/logs', methods=['GET'])
def logs():
    """Log from a contaniner.

    :return: Request 200 with results
    """
    data = request.args
    try:
        results = server_controller.logs(data)
    except Exception as e:
        return utils_server.manage_exceptions(e)

    return utils_server.make_json_response(200, results)


@app.route('/rm', methods=['PUT'])
def delete():
    """Delete a container.

    :return: Request 200 with results
    """
    data = json.loads(request.data)
    try:
        docker_out = server_controller.delete_container(data)
    except Exception as e:
        return utils_server.manage_exceptions(e)
    return utils_server.make_json_response(200, docker_out)


########################
### UN IMPLEMENTED ####
######################


@app.route('/stop', methods=['POST'])
def stop():
    data = json.loads(request.data)
    try:
        results = server_controller.stop_container(data)
    except Exception as e:
        return utils_server.manage_exceptions(e)
    return utils_server.make_json_response(200, results)


@app.route('/accounting', methods=['GET'])
def accounting():
    data = request.args
    try:
        results = server_controller.accounting(data)
    except Exception as e:
        return utils_server.manage_exceptions(e)
    return utils_server.make_json_response(200, results)


@app.route('/output', methods=['GET'])
def output():
    data = request.args
    try:
        results = server_controller.output(data)
    except Exception as e:
        return utils_server.manage_exceptions(e)
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
