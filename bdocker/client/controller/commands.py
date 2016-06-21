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
from bdocker.client.controller import utils as utils_cli
from bdocker.common import exceptions
from bdocker.common import modules, request
from bdocker.common import utils as utils_common

TOKEN_FILE_NAME = '.bdocker_token'


class CommandController(object):

    def __init__(self, endpoint=None):
        conf = utils_common.load_configuration_from_file()
        self.batch_module = modules.load_batch_module(conf)
        try:
            job_info = self.batch_module.get_job_info()
            if not endpoint:  # TODO(jorgesece): host should have http or https
                endpoint = 'http://%s:%s' % (
                    conf['server']['host'],
                    conf['server']['port']
                )
            cred_info = conf['credentials']
            self.defaul_token_name = (
                cred_info.get("token_client_file",
                              TOKEN_FILE_NAME)
            )
            self.job_info = job_info
            self.job_id = job_info["id"]
            self.token_file = "%s/%s_%s" % (
                job_info['home'],  # TODO(jorgesece): pop it
                self.defaul_token_name,
                self.job_id
            )
            self.user_name = job_info['user_name']
            self.token_storage = cred_info["token_store"]
            self.control = request.RequestController(endopoint=endpoint)
        except Exception as e:
            raise exceptions.ConfigurationException("Configuring server %s"
                                                    % endpoint
                                                    )

    def configuration(self, user_name=None, jobid=None):
        path = "/configuration"
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
        user_info.update({'job': self.job_info})
        parameters = {"admin_token": admin_token, "user_credentials": user_info}
        token = self.control.execute_post(path=path, parameters=parameters)
        utils_cli.write_user_credentials(token, self.token_file,
                                         user_info['uid'],
                                         user_info['gid'])
        return {"token": token, "path": self.token_file}

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
        user_info.update({'job': self.job_info})
        parameters = {"admin_token": admin_token, "user_credentials": user_info}
        token = self.control.execute_post(path=path, parameters=parameters)
        utils_cli.write_user_credentials(token, self.token_file,
                                         user_info['uid'],
                                         user_info['gid'])
        return {"token": token, "path": self.token_file}

    def clean_environment(self, token, force):
        path = "/clean"
        admin_token = utils_cli.get_admin_token(self.token_storage)
        token = utils_cli.token_parse(token, self.token_file)
        parameters = {"admin_token": admin_token, 'token': token,
                      "force": force}
        self.control.execute_delete(path=path, parameters=parameters)
        return token

    def batch_config(self, token):
        path = "/batchconf"
        admin_token = utils_cli.get_admin_token(self.token_storage)
        token = utils_cli.token_parse(token, self.token_file)
        parameters = {"admin_token": admin_token,
                      "token": token,
                      }
        out = self.control.execute_put(path=path, parameters=parameters)
        return out

    def batch_clean(self, token):
        # TODO(jorgesece): include in clean environment
        path = "/batchclean"
        admin_token = utils_cli.get_admin_token(self.token_storage)
        token = utils_cli.token_parse(token, self.token_file)
        parameters = {"admin_token": admin_token,
                      "token": token}
        self.control.execute_delete(path=path, parameters=parameters)

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

    def container_delete(self, token, container_ids, force=False):
        path = "/rm"
        token = utils_cli.token_parse(token, self.token_file)
        parameters = {"token": token, "container_id": container_ids,
                      "force": force}
        out = self.control.execute_put(path=path, parameters=parameters)
        return out

    def notify_accounting(self, token):
        path = "/notify_accounting"
        admin_token = utils_cli.get_admin_token(self.token_storage)
        token = utils_cli.token_parse(token, self.token_file)
        acc = self.batch_module.create_accounting(self.job_id)
        parameters = {"admin_token": admin_token,
                      'token': token,
                      'accounting': acc
                      }
        self.control.execute_put(path=path, parameters=parameters)
        return token

    def accounting_retrieve(self, token, container_id):
        path = "/accounting"
        token = utils_cli.token_parse(token, self.token_file)
        parameters = {"token": token, "container_id": container_id}
        results = self.control.execute_get(path=path, parameters=parameters)
        return results

    def container_inspect(self, token, container_id):
        path = "/inspect"
        token = utils_cli.token_parse(token, self.token_file)
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
