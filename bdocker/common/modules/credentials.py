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
import sys
import uuid

from bdocker.common import exceptions
from bdocker.common import utils as utils_common

sys.tracebacklimit = 0


class UserController(object):

    def __init__(self, path):
        # TODO(jorgesece): control refresh token
        self.path = path
        self.token_store = utils_common.read_yaml_file(path)

    def save_token_file(self):
        """Save token store in the file

        """
        utils_common.write_yaml_file(self.path, self.token_store)

    def _get_token_from_cache(self, token):
        # TODO(jorgesece): refresh from file?
        """Get token from token store

        :param token: token looked for
        """
        if token not in self.token_store:
            raise exceptions.UserCredentialsException(
                "User token not found")
        return self.token_store[token]

    def _set_token(self, user_info):
        """Storage token and user information in token store

        :param user_info: dict that include uid, and gid
        """
        token = uuid.uuid4().hex
        token_content = {
            'uid': user_info['uid'],
            'gid': user_info['gid'],
            'home': user_info['home']
        }
        if 'job' in user_info:
            token_content['job'] = {
                    "id": user_info['job']['id'],
                    "spool": user_info['job']['spool']
                }
        new_token = {token: token_content}
        self.token_store = utils_common.read_yaml_file(
            self.path
        )
        self.token_store.update(new_token)
        self.save_token_file()
        return token

    def _update_token(self, token, fields):
        """update field in the token store

        :param token: token of the registry
        :param fields: array of element to be updated
        """
        current_token = self._get_token_from_cache(token)
        for key, value in fields.items():
            current_token[key] = value
        self.token_store = utils_common.read_yaml_file(
            self.path
        )
        self.token_store.update({token: current_token})
        self.save_token_file()

    def get_token(self, token):
        return self._get_token_from_cache(token)

    def authenticate(self, admin_token, session_data):
        """Authenticates a user in the system.

        Creates a token record. It could be invoked by the administrator

        :param admin_token: administration token
        :param user_data: array of element to be updated
        """
        self.authorize_admin(admin_token)
        utils_common.check_user_credentials(session_data)
        try:
            token = self._set_token(session_data)
        except Exception as e:
            raise exceptions.UserCredentialsException(
                "Invalid user information")
        return token

    def authorize_admin(self, admin_token):
        """Clean token from token store

        :param admin_token: token looked for
        """
        prolog_token = self._get_token_from_cache("prolog")
        if admin_token != prolog_token['token']:
            raise exceptions.UserCredentialsException(
                "Unauthorized user with token: %s" % admin_token)

    def get_token_from_file(self, path, file_name, jobid):
        path = "%s/%s_%s" % (path, file_name, jobid)
        token = utils_common.read_user_credentials(path)
        return self._get_token_from_cache(token)

    def remove_token_from_cache(self, token):
        """remove token from token store

        :param token: token looked for
        """
        if token not in self.token_store:
            raise exceptions.UserCredentialsException(
                "Token not found")
        self.token_store = utils_common.read_yaml_file(
            self.path
        )
        del self.token_store[token]
        self.save_token_file()

    def add_image(self, token, image_id):
        """Add image to the token record.

        :param token: token
        :param image_id: image id from dockers
        """
        # todo: test this method
        current_token = self._get_token_from_cache(token)
        if "images" not in current_token:
            current_token["images"] = []
        if image_id not in current_token["images"]:
            current_token["images"].append(image_id)
            self._update_token(token, current_token)

    def remove_image(self, token, image_id):
        """Remove image to the token record.

        :param token: token
        :param image_id: image id from dockers
        """
        current_token = self._get_token_from_cache(token)
        if current_token["images"].__len__() > 1:
            current_token["images"].remove(image_id)
        else:
            del current_token["images"]
        self._update_token(token, current_token)

    def add_container(self, token, container_id):
        """Add container to the token record.

        :param token: token
        :param container_id: container id from dockers
        """
        current_token = self._get_token_from_cache(token)
        if "containers" in current_token:
            current_token["containers"].append(container_id)
        else:
            current_token["containers"] = [container_id]
        self._update_token(token, current_token)

    def remove_container(self, token, container_id):
        """Remove container to the token record.

        :param token: token
        :param container_id: container id from dockers
        """
        current_token = self._get_token_from_cache(token)
        if current_token["containers"].__len__() > 1:
            current_token["containers"].remove(container_id)
        else:
            del current_token["containers"]
        self._update_token(token, current_token)

    def list_containers(self, token):
        """Return containers from a token record.

        :param token: token
        """
        token_info = self._get_token_from_cache(token)
        if 'containers' not in token_info:
            return []
        return token_info['containers']

    def authorize_container(self, token, container_id):
        """Check user authorization to the container.

        :param token: user token
        :param container_id: container id
        """
        token_info = self._get_token_from_cache(token)
        if 'containers' not in token_info:
            raise exceptions.UserCredentialsException(
                "No container related to %s"
                % token)
        if container_id not in token_info['containers']:
            len = container_id.__len__()
            for c in token_info['containers']:
                if container_id == c[:len]:
                    return c
            raise exceptions.DockerException(
                message="No such container:"
                " %s " % container_id,
                code=404)
        return container_id

    def authorize_image(self, token, image_id):
        """Check user authorization to the container.

        :param token: user token
        :param image_id: image id
        """
        token_info = self._get_token_from_cache(token)
        if 'images' not in token_info:
            raise exceptions.UserCredentialsException(
                "No container related to %s"
                % token)
        if image_id not in token_info['images']:
            raise exceptions.DockerException(
                message="No such image:"
                " %s " % image_id,
                code=404)
        return True

    def authorize_directory(self, token, dir_path):
        """Check user authorization to the container.

        :param token: user token
        :param dir_path: directory for validation
        """
        # todo: add unittest
        token_info = self._get_token_from_cache(token)
        utils_common.validate_directory(dir_path, token_info['home_dir'])

    def authorize(self, token):
        """Check token authorization.

        :param token: user token
        """
        token_info = self._get_token_from_cache(token)
        return token_info

    def get_job_from_token(self, token):
        """Return the job of the token record.

        :param token: token
        """
        token_info = self._get_token_from_cache(token)
        if "job" not in token_info:
            raise exceptions.UserCredentialsException(
                "Job not found in token %s" % token)
        return token_info["job"]

    def update_job(self, token, job):
        """Update job of the token record.

        :param token: token updated
        """

        current_token = self._get_token_from_cache(token)
        if "job" not in current_token:
            raise exceptions.UserCredentialsException(
                "Job not found in token %s" % token)
        current_token["job"] = job
        self._update_token(token, current_token)
        return current_token

    def set_token_batch_info(self, token, batch_info):
        """Set job information related to the batch enviroment.

        :param token: token
        :param batch_info: information from the bath env
        """
        current_token = self._get_token_from_cache(token)
        current_token["job"].update(batch_info)
        self._update_token(token, current_token)