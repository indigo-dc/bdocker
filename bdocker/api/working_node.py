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

import flask

from bdocker import api
from bdocker.api import controller
from bdocker import utils


app = flask.Flask(__name__)


@app.route('/configuration', methods=['POST'])
def configuration():
    """Configure bdocker user environment.

      It creates the token and configure the batch
      system.

    :return: user_token
    """
    data = flask.request.get_json()
    try:
        user_token = get_server_controller().configuration(data)
    except Exception as e:
        return api.manage_exceptions(e)
    return api.make_json_response(
        201, user_token
    )


@app.route('/clean', methods=['DELETE'])
def clean():
    """Clean bdocker user environment.

      Delete the remaining containers and the token.
      In addition, it cleans the batch environment.

    :return: Request 204 with user_token
    """
    data = flask.request.args
    try:
        result = get_server_controller().clean(data)
    except Exception as e:
        return api.manage_exceptions(e)
    return api.make_json_response(204, [result])


@app.route('/pull', methods=['POST'])
def pull():
    """Pull request.

    Download a docker image from a repository

    :return: Request 201 with output
    """
    data = flask.request.get_json()
    try:
        result = get_server_controller().pull(data)
    except Exception as e:
        return api.manage_exceptions(e)
    return api.make_json_response(201, result)


@app.route('/run', methods=['PUT'])
def run():
    """Execute command in container.

    :return: Request 201 with results
    """
    data = flask.json.loads(flask.request.data)
    try:
        results = get_server_controller().run(data)
    except Exception as e:
        return api.manage_exceptions(e)
    return api.make_json_response(201, results)


@app.route('/ps', methods=['GET'])
def list_containers():
    """List containers.

    :return: Request 200 with results
    """
    data = flask.request.args
    try:
        results = get_server_controller().list_containers(data)
    except Exception as e:
        return api.manage_exceptions(e)
    return api.make_json_response(200, results)


@app.route('/inspect', methods=['GET'])
def show():
    """Show container information.

    :return: Request 200 with results
    """
    data = flask.request.args
    try:
        results = get_server_controller().show(data)
    except Exception as e:
        return api.manage_exceptions(e)
    return api.make_json_response(200, results)


@app.route('/logs', methods=['GET'])
def logs():
    """Log from a container.

    :return: Request 200 with results
    """
    data = flask.request.args
    try:
        results = get_server_controller().logs(data)
    except Exception as e:
        return api.manage_exceptions(e)

    return api.make_json_response(200, results)


@app.route('/rm', methods=['PUT'])
def delete():
    """Delete a container.

    :return: Request 201 with results
    """
    data = flask.json.loads(flask.request.data)
    try:
        docker_out = get_server_controller().delete_container(data)
    except Exception as e:
        return api.manage_exceptions(e)
    return api.make_json_response(200, docker_out)


@app.route('/notify_accounting', methods=['PUT'])
def notify_accounting():
    """Notify accounting.

     Send the accounting information to the
     accounting server.
     [DEPRECATED. It is included in the batch daemon]

    :return: Request 201 with results
    """

    data = flask.json.loads(flask.request.data)
    try:
        results = get_server_controller().notify_accounting(data)
    except Exception as e:
        return api.manage_exceptions(e)
    return api.make_json_response(201, results)


@app.route('/copy', methods=['PUT'])
def copy():
    """Copy file or folder to or from the docker filesystem.

    :return: Request 201 with results
    """
    data = flask.json.loads(flask.request.data)
    try:
        results = get_server_controller().copy(data)
    except Exception as e:
        return api.manage_exceptions(e)
    return api.make_json_response(201, results)


##############
# NO USED ####
##############
# This code is not by the command line client

@app.route('/stop', methods=['PUT'])
def stop():
    data = flask.json.loads(flask.request.data)
    try:
        results = get_server_controller().stop_container(data)
    except Exception as e:
        return api.manage_exceptions(e)
    return api.make_json_response(200, results)
    return flask.g.server_controller

##################
#  NO USED #######
##################


def load_configuration():
    return utils.load_configuration_from_file()


def init_server():
    return controller.ServerController(get_conf())


def get_conf():
    if not hasattr(flask.g, 'conf'):
        flask.g.conf = load_configuration()
    return flask.g.conf


def get_server_controller():
    if not hasattr(flask.g, 'server_controller'):
        flask.g.server_controller = init_server()
    return flask.g.server_controller

if __name__ == '__main__':
    with app.app_context():
        logging = get_conf()['server']['logging']
        port = int(get_conf()['server']['port'])
        host = get_conf()['server']['host']
        debug = False
        if logging == 'DEBUG':
            debug = True
        app.run(host=host,
                port=port,
                debug=debug)
