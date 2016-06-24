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

from bdocker import modules
from bdocker import server

LOG = logging.getLogger(__name__)


class AccountingServerController(object):
    def __init__(self, conf):
        self.credentials_module = modules.load_credentials_module(conf)
        self.batch_module = modules.load_batch_accounting_module(conf)

    def set_job_accounting(self, data):
        """ Update the accounting file using the incoming data
        :return: empty
        """
        required = {'admin_token',
                    "accounting"}
        server.validate(data, required)
        admin_token = data['admin_token']
        accounting = data["accounting"]
        self.credentials_module.authorize_admin(admin_token)
        data = self.batch_module.set_job_accounting(accounting)
        return data


class ServerController(object):
    def __init__(self, conf):
        self.credentials_module = modules.load_credentials_module(conf)
        self.batch_module = modules.load_batch_module(conf)
        self.docker_module = modules.load_docker_module(conf)

    def configuration(self, data):
        """Configure bdocker user environment.
          It creates the token and configure the batch
          system.

        :return: user_token
        """
        required = {'admin_token', 'user_credentials'}
        server.validate(data, required)
        admin_token = data['admin_token']
        session_data = data['user_credentials']
        user_token = self.credentials_module.authenticate(
            admin_token, session_data
        )
        LOG.info("Authentication. Token: %s" % user_token)

        batch_info = self.batch_module.conf_environment(
            session_data, admin_token
        )
        self.credentials_module.set_token_batch_info(
            user_token, batch_info
        )
        LOG.info("Batch system configured")
        return user_token

    def clean(self, data):
        """Clean bdocker user environment.
          Delete the remaining containers and the token.
          In addition, it cleans the batch environment.

        :return: user_token
        """
        required = {'admin_token', 'token'}
        server.validate(data, required)
        admin_token = data['admin_token']
        force = server.eval_bool(
            data.get('force', False)
        )
        self.credentials_module.authorize_admin(admin_token)
        token = data['token']
        containers = self.credentials_module.list_containers(token)
        if containers:
            self.docker_module.clean_containers(containers, force)
            LOG.info("Delete containers")

        token_info = self.credentials_module.get_token(token)
        self.batch_module.clean_environment(token_info, admin_token)
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
        server.validate(data, required)
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
        server.validate(data, required)
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
        server.validate(data, required)
        token = data['token']
        all_list = server.eval_bool(data.get('all', False))
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
        server.validate(data, required)
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
        server.validate(data, required)
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
        server.validate(data, required)
        token = data['token']
        container_ids = data['container_id']
        force = server.eval_bool(
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

    def notify_accounting(self, data):
        """Notify accounting.

        Send the accounting information to the accounting
        server. [DEPRECATED]

        :return: output
        """
        required = {'admin_token', 'token'}
        server.validate(data, required)
        admin_token = data['admin_token']
        self.credentials_module.authorize_admin(admin_token)
        token = data['token']
        job = self.credentials_module.get_job_from_token(token)
        accounting = self.batch_module.get_accounting(job['id'])
        job.update(accounting)
        self.credentials_module.update_job(token, job)
        self.batch_module.notify_accounting(admin_token, job)


    ########################
    ### UN IMPLEMENTED ####
    ######################

    def stop_container(self, data):
        required = {'token', 'container_id'}
        server.validate(data, required)
        token = data['token']
        container_id = data['container_id']
        self.credentials_module.authorize_container(token,
                                               container_id)
        results = self.docker_module.stop_container(
        container_id)
        return results

    def accounting(self, data):
        required = {'token'}
        server.validate(data, required)
        token = data['token']
        # todo: study the implementation
        token_info = self.credentials_module.authorize_container(token)
        results = self.docker_module.accounting_container(token_info)
        return results

    def output(self, data):
        required = {'token', 'container_id'}
        server.validate(data, required)
        token = data['token']
        container_id = data['container_id']
        self.credentials_module.authorize_container(token,
                                           container_id)
        results = self.docker_module.output_task(container_id)
        return results
