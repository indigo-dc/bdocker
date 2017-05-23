# -*- coding: utf-8 -*-

# Copyright 2015 LIP - INDIGO-DataCloud
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

import os
import pwd

from bdocker import exceptions
from bdocker import modules
from bdocker.modules import request
from bdocker import utils

TOKEN_FILE_NAME = '.bdocker_token'


def token_parse(value, path):
    """Parse token

    If value is null, it read the token from the
    $HOME/.bdocker_token_$JOBID file

    :param value: token value
    :param path: path from with read the token
    """
    try:
        if not value:
            value = utils.read_file(path)
        return value
    except BaseException:
        raise exceptions.UserCredentialsException(
            "Token can not be found in %s " % path
        )


def get_user_credentials(name):
    """Read user information from user

    :param name: name of the user
    """
    try:
        info = pwd.getpwnam(name)
        home_dir = os.path.realpath(info.pw_dir)
        user = {'uid': info.pw_uid, 'gid': info.pw_gid,
                'home': home_dir}
    except BaseException:
        raise exceptions.UserCredentialsException(
            "User %s not found: " % name
        )
    return user


def write_user_credentials(token, file_path,
                           uid=None, gid=None):
    """Write token in file and change its owner,

    :param token: token ID
    :param file_path: file to write it
    :param uid: user id
    :param gid: user group id
    """
    out = open(file_path, 'w')
    out.write(token)
    # set_environ('BDOCKER_TOKEN_FILE',
    # file_path)
    out.close()
    if uid:
        os.chown(file_path, uid, gid)


class CommandController(object):
    """Command line controller class."""

    def __init__(self, endpoint=None):
        self.conf = utils.load_configuration_from_file()
        self.batch_module = modules.load_batch_module(self.conf)
        try:
            if not endpoint:  # TODO(jorgesece): host should have http or https
                endpoint = 'http://%s:%s' % (
                    self.conf['server']['host'],
                    self.conf['server']['port']
                )
            cred_info = self.conf['credentials']
            self.defaul_token_name = (
                cred_info.get("token_client_file",
                              TOKEN_FILE_NAME)
            )
            self.token_storage = cred_info["token_store"]
            self.control = request.RequestController(endopoint=endpoint)
        except BaseException as e:
            raise exceptions.ConfigurationException(
                message="", exc=e
            )

    def _get_job_info(self):
        """Return the job information

        :return: dictionary with job information
        """
        job_info = self.batch_module.get_job_info()
        return job_info

    def _get_token_file(self, user_name, job_id):
        """Return the token file path.

        :param user_name: user name
        :param job_id: job id
        :return:
        """
        token_file = "%s/%s_%s" % (
            user_name,
            self.defaul_token_name,
            job_id
        )
        return token_file

    def configuration(self, user_name=None):
        """Configures the job session.

        It validates the admin user and creates the job session.

        :param user_name:
        :return:
        """
        path = "/configuration"
        credential_module = modules.load_credentials_module(self.conf)
        admin_token = credential_module.get_admin_token()
        # TODO(jorgesece): job information retrieval when implement the
        # pararell/mpi version
        job_info = self._get_job_info()
        if user_name:
            user_info = get_user_credentials(user_name)
        else:
            user_info = get_user_credentials(
                job_info['user_name']
            )
        token_file = self._get_token_file(user_info.get("home"),
                                          job_info['job_id'])

        user_info.update({'job': job_info})
        parameters = {"admin_token": admin_token,
                      "user_credentials": user_info}
        token = self.control.execute_post(path=path, parameters=parameters)
        write_user_credentials(token, token_file,
                               user_info['uid'],
                               user_info['gid'])
        return {"token": token, "path": token_file}

    def clean_environment(self, token):
        """Clean credentials and batch environment.

        It cleans a token credential for the user, and
        the batch environment, in addition to delete all
        dockers. Also, Command executed by the root in prolog

        :param token:
        :return:
        """
        path = "/clean"
        credential_module = modules.load_credentials_module(self.conf)
        admin_token = credential_module.get_admin_token()
        if not token:
            job_info = self._get_job_info()
            token_file = self._get_token_file(job_info["home"],
                                              job_info['job_id'])
            token = token_parse(token, token_file)
        else:
            token_info = credential_module.get_token(token)
            token_file = self._get_token_file(token_info["home"],
                                              token_info['job']['job_id']
                                              )
        parameters = {"admin_token": admin_token, 'token': token}
        self.control.execute_delete(path=path, parameters=parameters)
        os.remove(token_file)
        return token

    def container_pull(self, token, source):
        """Pull image.

        This method get the token from the HOME file and make the pull request.

        :param token: token (optional)
        :param source: image repository
        :return: dictionary with results
        """
        path = "/pull"
        job_info = self._get_job_info()
        token_file = self._get_token_file(job_info["home"],
                                          job_info['job_id'])
        token = token_parse(token, token_file)
        parameters = {"token": token, "source": source}
        results = self.control.execute_post(path=path, parameters=parameters)
        return results

    def container_run(self, token, image_id, detach, script,
                      working_dir=None, volume=None):
        """Run container.

        This method get the token from the HOME file and make the run request.

        :param token: token (optional)
        :param image_id: image id
        :param detach: boolean to detach the container execution
        :param script: script to execute
        :param working_dir: working dir
        :param volume: volume to bind
        :return: dictionary with results
        """
        path = "/run"
        job_info = self._get_job_info()
        token_file = self._get_token_file(job_info["home"],
                                          job_info['job_id'])
        token = token_parse(token, token_file)
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

    def container_list(self, token, all_containers=False):
        """List containers

        This method get the token from the HOME file and make the ps request.

        :param token: token (optional)
        :param all_containers: all containers (optional)
        :return:
        """
        path = "/ps"
        job_info = self._get_job_info()
        token_file = self._get_token_file(job_info["home"],
                                          job_info['job_id'])
        token = token_parse(token, token_file)
        parameters = {"token": token, "all": all_containers}
        results = self.control.execute_get(path=path, parameters=parameters)

        return results

    def container_logs(self, token, container_id):
        """Show container log

        This method get the token from the HOME file and make the
        logs request.

        :param token: token optional
        :param container_id: container id
        :return:
        """
        path = "/logs"
        job_info = self._get_job_info()
        token_file = self._get_token_file(job_info["home"],
                                          job_info['job_id'])
        token = token_parse(token, token_file)
        parameters = {"token": token, "container_id": container_id}
        results = self.control.execute_get(path=path, parameters=parameters)
        return results

    def container_delete(self, token, container_ids, force=False):
        """Delete container

        This method get the token from the HOME file and make the
        rm request.

        :param token: token (optional)
        :param container_ids: container list
        :param force: boolean to force deletion (optional)
        :return:
        """
        path = "/rm"
        job_info = self._get_job_info()
        token_file = self._get_token_file(job_info["home"],
                                          job_info['job_id'])
        token = token_parse(token, token_file)
        parameters = {"token": token, "container_id": container_ids,
                      "force": force}
        out = self.control.execute_put(path=path, parameters=parameters)
        return out

    def notify_accounting(self, token):
        """Notify accounting

        This method get the token from the HOME file and make the
        notify_accounting request. This function is not used [DEPRECATED]

        :param token: token (optional)
        :return:
        """
        path = "/notify_accounting"
        credential_module = modules.load_credentials_module(self.conf)
        admin_token = credential_module.get_admin_token()
        job_info = self._get_job_info()
        token_file = self._get_token_file(job_info["home"],
                                          job_info['job_id'])
        token = token_parse(token, token_file)
        acc = self.batch_module.create_accounting(job_info['job_id'])
        parameters = {"admin_token": admin_token,
                      'accounting': acc
                      }
        self.control.execute_put(path=path, parameters=parameters)
        return token

    def accounting_retrieve(self, token, container_id):
        """Retrieve accounting.

        This method get the token from the HOME file and make the
        accounting request.

        :param token: token (optional)
        :param container_id: container id
        :return:
        """
        path = "/accounting"
        job_info = self._get_job_info()
        token_file = self._get_token_file(job_info["home"],
                                          job_info['job_id'])
        token = token_parse(token, token_file)
        parameters = {"token": token, "container_id": container_id}
        results = self.control.execute_get(path=path, parameters=parameters)
        return results

    def container_inspect(self, token, container_id):
        """Container details.

        This method get the token from the HOME file and make the
        inspect request.
        Show container details.

        :param token: token (optional)
        :param container_id: container id
        :return:
        """
        path = "/inspect"
        job_info = self._get_job_info()
        token_file = self._get_token_file(job_info["home"],
                                          job_info['job_id'])
        token = token_parse(token, token_file)
        parameters = {"token": token, "container_id": container_id}
        results = self.control.execute_get(path=path, parameters=parameters)
        return results

    def copy_to_from_container(self, token, container_id,
                               container_path,
                               host_path,
                               host_to_container):
        """Copy between container and host file system.

        This method get the token from the HOME file and make the
        copy request. Copy files from or to the container.

        :param token: token (optional)
        :param container_id: container id
        :param container_path: file path in container
        :param host_path: file path in the host
        :param host_to_container: boolean indicates the sense of copy
        :return:
        """
        path = "/copy"
        job_info = self._get_job_info()
        token_file = self._get_token_file(job_info["home"],
                                          job_info['job_id'])
        token = token_parse(token, token_file)
        parameters = {"token": token,
                      "container_id": container_id,
                      "container_path": container_path,
                      "host_path": host_path,
                      "host_to_container": host_to_container}
        results = self.control.execute_put(path=path, parameters=parameters)
        return results

    def container_stop(self, token, container_id):
        """Stop container.

        This method get the token from the HOME file and make the
        container stop request.

        :param token: token (optional)
        :param container_id: container id
        :return:
        """
        path = "/stop"
        job_info = self._get_job_info()
        token_file = self._get_token_file(job_info["home"],
                                          job_info['job_id'])
        token = token_parse(token, token_file)
        parameters = {"token": token,
                      "container_id": container_id}
        results = self.control.execute_put(path=path, parameters=parameters)
        return results

    def docker_info(self, token):
        """Docker information.

        This method get the token from the HOME file and make
        requests Docker information.

        :param token: token (optional)
        :return:
        """
        path = "/info"
        job_info = self._get_job_info()
        token_file = self._get_token_file(job_info["home"],
                                          job_info['job_id'])
        token = token_parse(token, token_file)
        parameters = {"token": token}
        results = self.control.execute_get(path=path, parameters=parameters)
        return results

    def container_start(self, token, container_id):
        """Starts container.

        This method get the token from the HOME file and make the
        container start request.

        :param token: token (optional)
        :param container_id: container id
        :return:
        """
        path = "/start"
        job_info = self._get_job_info()
        token_file = self._get_token_file(job_info["home"],
                                          job_info['job_id'])
        token = token_parse(token, token_file)
        parameters = {"token": token,
                      "container_id": container_id}
        results = self.control.execute_put(path=path, parameters=parameters)
        return results
