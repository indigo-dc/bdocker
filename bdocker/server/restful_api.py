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
from flask import json, request
import logging

from bdocker.common import exceptions
from bdocker.common import modules as modules_common
from bdocker.common import utils as utils_common
from bdocker.server import utils as utils_server

conf = utils_common.load_configuration_from_file()
credentials_module = modules_common.load_credentials_module(conf)
batch_module = modules_common.load_batch_module(conf)
docker_module = modules_common.load_docker_module(conf)

app = Flask(__name__)

LOG = logging.getLogger(__name__)

utils_server.set_error_handler(app)


@app.route('/credentials', methods=['POST'])
def credentials():
    data = request.get_json()
    required = {'token', 'user_credentials'}
    try:
        utils_server.validate(data, required)
        token = data['token']
        user = data['user_credentials']
        results = credentials_module.authenticate(token, user)
        return utils_server.make_json_response(201, results)
    except Exception as e:
            return utils_server.manage_exceptions(e)


@app.route('/clean', methods=['DELETE'])
def clean():
    data = request.args
    required = {'admin_token', 'token'}
    try:
        utils_server.validate(data, required)
        admin_token = data['admin_token']
        force = utils_server.eval_bool(
            data.get('force', False)
        )
        credentials_module.authorize_admin(admin_token)
        token = data['token']
        containers = credentials_module.list_containers(token)
        if containers:
            docker_module.clean_containers(containers, force)
        credentials_module.remove_token_from_cache(token)
        return utils_server.make_json_response(204, [token])
    except Exception as e:
        return utils_server.manage_exceptions(e)


@app.route('/pull', methods=['POST'])
def pull():
    data = request.get_json()
    required = {'token','source'}
    try:
        utils_server.validate(data, required)
        token = data['token']
        repo = data['source']
        credentials_module.authorize(token)
        result = docker_module.pull_image(repo)
        # credentials_module.add_image(token, result['image_id'])
        output = utils_server.make_json_response(201, result)
        return output
    except Exception as e:
            return utils_server.manage_exceptions(e)


@app.route('/run', methods=['PUT'])
def run():
    data = json.loads(request.data)
    required = {'token','image_id', 'script'}
    try:
        utils_server.validate(data, required)
        token = data['token']
        image_id = data['image_id']
        script = data['script']
        detach = data.get('detach', False)
        host_dir = data.get('host_dir', None)
        docker_dir = data.get('docker_dir', None)
        working_dir = data.get('working_dir', None)
        cgroup = data.get('cgroup', None)
        # TODO(jorgesece): control image private
        # credentials_module.authorize_image(
        #     token,
        #     image_id
        # )
        if host_dir:
            credentials_module.authorize_directory(token, host_dir)
        container_id = docker_module.run_container(
            image_id,
            detach,
            script,
            host_dir=host_dir,
            docker_dir=docker_dir,
            working_dir=working_dir,
            cgroup=cgroup
        )
        credentials_module.add_container(token, container_id)
        docker_module.start_container(container_id)
        if not detach:
            results = docker_module.logs_container(container_id)
        else:
            results = container_id
        return utils_server.make_json_response(201, results)
    except Exception as e:
        return utils_server.manage_exceptions(e)


@app.route('/ps', methods=['GET'])
def list_containers():
    data = request.args
    required = {'token'}
    try:
        utils_server.validate(data, required)
        token = data['token']
        all_list = utils_server.eval_bool(data.get('all', False))
        containers = credentials_module.list_containers(token)
        results = []
        if containers:
            results = docker_module.list_containers(containers,
                                                    all=all_list)
        return utils_server.make_json_response(200, results)
    except Exception as e:
        return utils_server.manage_exceptions(e)


@app.route('/inspect', methods=['GET'])
def show():
    data = request.args
    required = {'token'}
    try:
        utils_server.validate(data, required)
        token = data['token']
        container_id = data['container_id']
        c_id = credentials_module.authorize_container(
            token,
            container_id)
        results = docker_module.container_details(c_id)
        return utils_server.make_json_response(200, results)
    except Exception as e:
        return utils_server.manage_exceptions(e)

@app.route('/logs', methods=['GET'])
def logs():
    data = request.args
    required = {'token'}
    try:
        utils_server.validate(data, required)
        token = data['token']
        container_id = data['container_id']
        credentials_module.authorize_container(token,
                                               container_id)
        results = docker_module.logs_container(container_id)
        return utils_server.make_json_response(200, results)
    except Exception as e:
        return utils_server.manage_exceptions(e)


@app.route('/rm', methods=['PUT'])
def delete():
    data = json.loads(request.data)
    required = {'token', 'container_id'}
    try:
        utils_server.validate(data, required)
        token = data['token']
        container_ids = data['container_id']
        force = utils_server.eval_bool(
            data.get('force', False)
        )
        docker_out = []
        if not isinstance(container_ids, list):
            container_ids = [container_ids]
        for c_id in container_ids:
            try:
                full_id = credentials_module.authorize_container(
                    token,
                    c_id)
                docker_module.delete_container(full_id, force)
                credentials_module.remove_container(token, full_id)
                docker_out.append(full_id)
            except BaseException as e:
                LOG.exception(e.message)
                docker_out.append(e.message)
        return utils_server.make_json_response(200, docker_out)
    except Exception as e:
        return utils_server.manage_exceptions(e)


########################
### UN IMPLEMENTED ####
######################


@app.route('/stop', methods=['POST'])
def stop():
    data = json.loads(request.data)
    required = {'token','container_id'}
    utils_server.validate(data, required)
    token = data['token']
    container_id = data['container_id']
    credentials_module.authorize_container(token,
                                           container_id)
    results = docker_module.stop_container(
        container_id)
    return utils_server.make_json_response(200, results)


@app.route('/accounting', methods=['GET'])
def accounting():
    data = request.args
    required = {'token'}
    utils_server.validate(data, required)
    token = data['token']
    # todo: study the implementation
    token_info = credentials_module.authorize(token)
    results = docker_module.accounting_container(token_info)
    return utils_server.make_json_response(200, results)


@app.route('/output', methods=['GET'])
def output():
    data = request.args
    required = {'token','container_id'}
    utils_server.validate(data, required)
    token = data['token']
    container_id = data['container_id']
    credentials_module.authorize_container(token,
                                           container_id)
    results = docker_module.output_task(container_id)
    return utils_server.make_json_response(200, results)


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
