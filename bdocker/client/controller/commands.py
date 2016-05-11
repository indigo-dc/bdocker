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
from bdocker.common import exceptions
from bdocker.common import utils as utils_common
from bdocker.client.controller import utils


class CommandController(object):

    def __init__(self, conf_file=None):
        conf = utils_common.load_configuration(conf_file)
        try:
            endpoint = "http://%s:%s" % (conf['server']['host'],
                                         conf['server']['port'])
            self.control = request.RequestController(endopoint=endpoint)
            self.token_file = conf["credentials"]['token_client_file']
            self.token_storage = conf["credentials"]['token_store']
        except Exception as e:
            raise exceptions.ConfigurationException("Reading file: %s" % conf_file)

    def create_credentials(self, uid):
        path = "/credentials"
        user_info = utils.get_user_credentials(uid)
        home_dir = user_info.pop('home')
        admin_token = utils.get_admin_token(self.token_storage)
        parameters = {"token": admin_token, "user_credentials": user_info}
        result = self.control.execute_put(path=path, parameters=parameters)
        token = result
        token_path = "%s/%s" % (home_dir, self.token_file)
        utils.write_user_credentials(result, token_path)
        return {"token": token, "path": token_path}

    def container_pull(self, token, source):
        path = "/pull"
        parameters = {"token": token, "source": source}

        results = self.control.execute_put(path=path, parameters=parameters)
        return results

    def container_run(self, token, image_id, detach, script, volume=None):
        path = "/run"
        parameters = {"token": token,
                      "image_id": image_id,
                      "script": script,
                      "detach": detach,
                      }
        if volume:
          parameters["host_dir"] = volume["host_dir"]
          parameters["docker_dir"] = volume["docker_dir"]
        # -v /root/docker_test/:/tmp
        results = self.control.execute_post(path=path, parameters=parameters)
        return results

    # def container_run(self, token, image_id, script):
    # todo: create a run for a container that already exists
    #     path = "/run"
    #     parameters = {"token": token,
    #                   "image_id": image_id,
    #                   "script": script
    #                   }
    #     results = self.control.execute_post(path=path, parameters=parameters)
    #     return {"container_id": container_id, "error": err}

    def container_delete(self, token, container_id):
        path = "/delete"
        parameters = {"token": token, "container_id": container_id}
        self.control.execute_delete(path=path, parameters=parameters)
        # todo(jorgesece): implement message output
        message = "OK"
        return message

    def container_list(self, token, all=False):
        path = "/ps"
        parameters = {"token": token, "all":all}
        results = self.control.execute_get(path=path, parameters=parameters)

        return results

    def container_logs(self, token, container_id):
        path = "/logs"
        parameters = {"token": token, "container_id": container_id}
        results = self.control.execute_get(path=path, parameters=parameters)
        # todo(jorgesece): implement message output
        return results

    def accounting_retrieve(self, token, container_id):
        path = "/accounting"
        parameters = {"token": token, "container_id": container_id}
        results = self.control.execute_get(path=path, parameters=parameters)
        # todo(jorgesece): implement message output
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