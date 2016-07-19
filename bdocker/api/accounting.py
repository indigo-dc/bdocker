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


@app.route('/set_accounting', methods=['PUT'])
def set_job_accounting():
    """Register job accounting in the master.

    :return: 201
    """
    data = flask.request.get_json()
    try:
        data = get_server_controller().set_job_accounting(data)
    except Exception as e:
        return api.manage_exceptions(e)
    return api.make_json_response(
        201, data
    )


def load_configuration():
    return utils.load_configuration_from_file()


def init_server():
    c = get_conf()
    return controller.AccountingServerController(c)


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
        environ = get_conf()['server']['environ']
        port = int(get_conf()['server']['port'])
        host = get_conf()['server']['host']
        debug = False
        if environ == 'DEBUG':
            debug = True
        app.run(host=host,
                port=port,
                debug=debug)
