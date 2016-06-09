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

from bdocker.common import exceptions
from bdocker.common import modules as modules_common
from bdocker.server import utils as utils_server

LOG = logging.getLogger(__name__)


class ServerController(object):
    def __init__(self, conf):
        self.credentials_module = modules_common.load_credentials_module(conf)
        self.batch_module = modules_common.load_batch_module(conf)
        self.docker_module = modules_common.load_docker_module(conf)

    def configuration(self, data):
        """Configure bdocker user environment.
          It creates the token and configure the batch
          system.

        :return: user_token
        """
        required = {'admin_token', 'user_credentials'}
        utils_server.validate(data, required)
        admin_token = data['admin_token']
        user = data['user_credentials']
        try:
            job_id = user["job"]['id']
            job_spool = user['job']['spool']
        except KeyError as e:
            message = ("Job information error %s"
                       % e.message)
            raise exceptions.ParseException(message=message)
        user_token = self.credentials_module.authenticate(
            admin_token, user
        )
        LOG.info("Authentication. Token: %s" % user_token)

        batch_info = self.batch_module.conf_environment(
            job_id, job_spool
        )
        self.credentials_module.set_token_batch_info(user_token, batch_info)
        LOG.info("Batch system configured")
        return user_token


    def credentials(self, data):
        """ Create user token environment
        DEPRECATED. Included in clean
        :return:
        """
        required = {'admin_token', 'user_credentials'}
        utils_server.validate(data, required)
        try:
            token = data['admin_token']
            user = data['user_credentials']
            user_token = self.credentials_module.authenticate(token, user)
            LOG.info("Authentication. Token: %s" % user_token)
            return user_token
        except Exception as e:
                return utils_server.manage_exceptions(e)

    def batch_configuration(self, data):
        """ Config batch system environment
        DEPRECATED. Included in clean
        :return:
        """
        required = {'admin_token', 'token'}
        utils_server.validate(data, required)
        admin_token = data['admin_token']
        token = data['token']
        self.credentials_module.authorize_admin(admin_token)
        job = self.credentials_module.get_job_from_token(token)
        try:
            job_id = job['id']
            job_spool = job['spool']
        except KeyError as e:
            message = ("Job information error %s"
                       % e.message)
            raise exceptions.ParseException(message=message)
        batch_info = self.batch_module.conf_environment(
            job_id, job_spool
        )
        self.credentials_module.set_token_batch_info(token, batch_info)
        LOG.info("Batch system configured")

    def batch_clean(self, data):
        """ Clean batch system environment
        DEPRECATED. Included in clean
        :return:
        """
        required = {'admin_token', 'token'}
        utils_server.validate(data, required)
        admin_token = data['admin_token']
        token = data['token']
        self.credentials_module.authorize_admin(admin_token)
        job = self.credentials_module.get_job_from_token(token)
        self.batch_module.clean_environment(job['id'])
        return []

    def clean(self, data):
        """Clean bdocker user environment.
          Delete the remaining containers and the token.
          In addition, it cleans the batch environment.

        :return: user_token
        """
        required = {'admin_token', 'token'}
        utils_server.validate(data, required)
        admin_token = data['admin_token']
        force = utils_server.eval_bool(
            data.get('force', False)
        )
        self.credentials_module.authorize_admin(admin_token)
        token = data['token']
        containers = self.credentials_module.list_containers(token)
        if containers:
            self.docker_module.clean_containers(containers, force)
            LOG.info("Delete containers")

        job = self.credentials_module.get_job_from_token(token)
        self.batch_module.clean_environment(job['id'])
        LOG.info("Batch system cleaned")
        self.credentials_module.remove_token_from_cache(token)
        LOG.info("Delete token: %s" % token)
        return token


    def pull(self, data):
        """Pull request.
        Download a docker image from a repository

        :return: output
        """
        required = {'token', 'source'}
        utils_server.validate(data, required)
        token = data['token']
        repo = data['source']
        self.credentials_module.authorize(token)
        result = self.docker_module.pull_image(repo)
        # credentials_module.add_image(token, result['image_id'])
        return result


    def run(self, data):
        """Execute command in container.

        :return: Request 201 with results
        """
        required = {'token','image_id', 'script'}
        utils_server.validate(data, required)
        token = data['token']
        image_id = data['image_id']
        script = data['script']
        detach = data.get('detach', False)
        host_dir = data.get('host_dir', None)
        docker_dir = data.get('docker_dir', None)
        working_dir = data.get('working_dir', None)
        # cgroup = data.get('cgroup', None)
        # TODO(jorgesece): control image private
        # credentials_module.authorize_image(
        #     token,
        #     image_id
        # )
        if host_dir:
            self.credentials_module.authorize_directory(token, host_dir)
        job_info = self.credentials_module.get_job_from_token(token)
        cgroup_parent = job_info.get('cgroup', None)
        container_id = self.docker_module.run_container(
        image_id,
        detach,
        script,
        host_dir=host_dir,
        docker_dir=docker_dir,
        working_dir=working_dir,
        cgroup=cgroup_parent
        )
        self.credentials_module.add_container(token, container_id)
        self.docker_module.start_container(container_id)
        if not detach:
            results = self.docker_module.logs_container(container_id)
        else:
            results = container_id
        return  results


    def list_containers(self, data):
        """List containers.

        :return: Request 200 with results
        """
        required = {'token'}
        utils_server.validate(data, required)
        token = data['token']
        all_list = utils_server.eval_bool(data.get('all', False))
        containers = self.credentials_module.list_containers(token)
        results = []
        if containers:
            results = self.docker_module.list_containers(containers,
                                                    all=all_list)
        return results


    def show(self, data):
        """Show container information.

        :return: Request 200 with results
        """
        required = {'token', 'container_id'}
        utils_server.validate(data, required)
        token = data['token']
        container_id = data['container_id']
        c_id = self.credentials_module.authorize_container(
            token,
            container_id)
        results = self.docker_module.container_details(c_id)
        return results


    def logs(self, data):
        """Log from a contaniner.

        :return: Request 200 with results
        """
        required = {'token', 'container_id'}
        utils_server.validate(data, required)
        token = data['token']
        container_id = data['container_id']
        self.credentials_module.authorize_container(token,
                                                    container_id)
        results = self.docker_module.logs_container(container_id)
        return results

    def delete_container(self, data):
        """Delete a container.

        :return: Request 200 with results
        """
        required = {'token', 'container_id'}
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
                full_id = self.credentials_module.authorize_container(
                    token,
                    c_id)
                self.docker_module.delete_container(full_id, force)
                self.credentials_module.remove_container(token, full_id)
                docker_out.append(full_id)
            except BaseException as e:
                LOG.exception(e.message)
                docker_out.append(e.message)
        return docker_out


    ########################
    ### UN IMPLEMENTED ####
    ######################

    def stop_container(self, data):
        required = {'token', 'container_id'}
        utils_server.validate(data, required)
        token = data['token']
        container_id = data['container_id']
        self.credentials_module.authorize_container(token,
                                               container_id)
        results = self.docker_module.stop_container(
        container_id)
        return results

    def accounting(self, data):
        required = {'token'}
        utils_server.validate(data, required)
        token = data['token']
        # todo: study the implementation
        token_info = self.credentials_module.authorize_container(token)
        results = self.docker_module.accounting_container(token_info)
        return results

    def output(self, data):
        required = {'token', 'container_id'}
        utils_server.validate(data, required)
        token = data['token']
        container_id = data['container_id']
        self.credentials_module.authorize_container(token,
                                           container_id)
        results = self.docker_module.output_task(container_id)
        return results
