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

import logging

import flask

from bdocker import api
from bdocker.api import controller
from bdocker import utils

conf = utils.load_configuration_from_file()
server_controller = controller.AccountingServerController(conf)

app = flask.Flask(__name__)

LOG = logging.getLogger(__name__)

api.set_error_handler(app)


@app.route('/set_accounting', methods=['PUT'])
def set_job_accounting():
    """Register job accounting in the master.

    :return: 201
    """
    data = flask.request.get_json()
    try:
        data = server_controller.set_job_accounting(data)
    except Exception as e:
        return api.manage_exceptions(e)
    return api.make_json_response(
        201, data
    )


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
