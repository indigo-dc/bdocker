# -*- coding: utf-8 -*-

# Copyright 2016 LIP - Lisbon
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
from bdocker.client.controller import request
from bdocker.client.controller import utils as utils_cli
from bdocker.common import modules
from bdocker.common import exceptions
from bdocker.common import utils as utils_common


class CommandController(object):

    def __init__(self, endpoint=None):
        conf = utils_common.load_configuration_from_file()
        batch_module = modules.load_batch_module(conf)
        try:
            job_info = batch_module.get_job_info()
            if not endpoint:
                endpoint = 'http://%s:%s' % (
                    conf['server']['host'],
                    conf['server']['port']
                )
            self.defaul_token_name = (
                conf['credentials']["token_client_file"]
            )
            self.job_id = job_info["job_id"]
            self.token_file = "%s/%s_%s" % (
                job_info['home'],
                self.defaul_token_name,
                self.job_id
            )
            self.user_name = job_info['user']
            self.token_storage = conf['credentials']["token_store"]
            self.control = request.RequestController(endopoint=endpoint)
        except Exception as e:
            raise exceptions.ConfigurationException("Configuring server %s"
                                                    % endpoint
                                                    )

    def create_credentials(self, user_name=None, jobid=None):
        path = "/credentials"
        admin_token = utils_cli.get_admin_token(self.token_storage)
        if user_name:
            self.user_name = user_name
            user_info = utils_cli.get_user_credentials(self.user_name)
            self.token_file = "%s/%s_%s" % (
                user_info.get("home"),
                self.defaul_token_name,
                self.job_id
            )
        else:
            user_info = utils_cli.get_user_credentials(self.user_name)
        user_info.update({'jobid': self.job_id})
        parameters = {"token": admin_token, "user_credentials": user_info}
        token = self.control.execute_post(path=path, parameters=parameters)
        utils_cli.write_user_credentials(token, self.token_file,
                                         user_info['uid'])
        return {"token": token, "path": self.token_file}

    def clean_environment(self, token):
        path = "/clean"
        admin_token = utils_cli.get_admin_token(self.token_storage)
        token = utils_cli.token_parse(token, self.token_file)
        parameters = {"admin_token": admin_token, 'token': token}
        self.control.execute_delete(path=path, parameters=parameters)
        return token

    def container_pull(self, token, source):
        path = "/pull"
        token = utils_cli.token_parse(token, self.token_file)
        parameters = {"token": token, "source": source}
        results = self.control.execute_post(path=path, parameters=parameters)
        return results

    def container_run(self, token, image_id, detach, script,
                      working_dir=None, volume=None):
        path = "/run"
        token = utils_cli.token_parse(token, self.token_file)
        parameters = {"token": token,
                      "image_id": image_id,
                      "script": script,
                      "detach": detach,
                      }
        if volume:
            parameters["host_dir"] = volume["host_dir"]
            parameters["docker_dir"] = volume["docker_dir"]
        if working_dir:
            parameters["working_dir"] = working_dir
        results = self.control.execute_put(path=path, parameters=parameters)
        return results

    def container_list(self, token, all=False):
        path = "/ps"
        token = utils_cli.token_parse(token, self.token_file)
        parameters = {"token": token, "all": all}
        results = self.control.execute_get(path=path, parameters=parameters)

        return results

    def container_logs(self, token, container_id):
        path = "/logs"
        token = utils_cli.token_parse(token, self.token_file)
        parameters = {"token": token, "container_id": container_id}
        results = self.control.execute_get(path=path, parameters=parameters)
        return results

    def container_delete(self, token, container_id):
        path = "/rm"
        token = utils_cli.token_parse(token, self.token_file)
        parameters = {"token": token, "container_id": container_id}
        self.control.execute_delete(path=path, parameters=parameters)
        return container_id

    def accounting_retrieve(self, token, container_id):
        path = "/accounting"
        token = utils_cli.token_parse(token, self.token_file)
        parameters = {"token": token, "container_id": container_id}
        results = self.control.execute_get(path=path, parameters=parameters)
        return results

    def container_inspect(self, token, container_id):
        path = "/inspect"
        token = utils_cli.token_parse(token, self.home_token_file)
        parameters = {"token": token, "container_id": container_id}
        results = self.control.execute_get(path=path, parameters=parameters)
        return results

    # def container_start(self, token, container_id):
    #     path = "/start"
    #     parameters = {"token": token, "container_id": container_id}
    #     results = self.control.execute_post(path=path, parameters=parameters)
    #     # todo(jorgesece): implement message output
    #     return results
    #
    #
    # def container_stop(self, token, container_id):
    #     path = "/stop"
    #     parameters = {"token": token, "container_id": container_id}
    #     results = self.control.execute_post(path=path, parameters=parameters)
    #     # todo(jorgesece): implement message output
    #     return results
