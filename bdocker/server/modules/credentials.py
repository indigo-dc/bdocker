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

import uuid

from bdocker.common import exceptions
from bdocker.server.modules import utils


class UserController(object):

    def __init__(self, path):
        self.path = path
        self.token_store = utils.read_yaml_file(path)

    def _save_token_file(self):
        """Save token store in the file

        """
        utils.write_yaml_file(self.path, self.token_store)

    def _get_token_from_cache(self, token):
        """Get token from token store

        :param token: token looked for
        """
        if token not in self.token_store:
            raise exceptions.UserCredentialsException(
                "Token not found")
        return self.token_store[token]

    def _set_token_in_cache(self, user_info):
        """Storage token and user information in token store

        :param user_info: dict that include uid, and gid
        """
        token = uuid.uuid4().hex
        new_token = {token: {
                            'uid': user_info['uid'],
                            'gid': user_info['gid'],
                            }
                    }
        self.token_store.update(new_token)
        return token

    def _update_token_in_cache(self, token, fields):
        """update field in the token record

        :param token: token of the registry
        :param fields: array of element to be updated
        """
        current_token = self._get_token_from_cache(token)
        for key, value in fields.items():
            current_token[key] = value
        self.token_store.update({token: current_token})

    def authenticate(self, admin_token, user_data):
        """Authenticates a user in the system.

        Creates a token record. It could be invoked by the administrator

        :param master_token: administration token
        :param user_data: array of element to be updated
        """
        prolog_token = self._get_token_from_cache("prolog")
        if admin_token != prolog_token['token']:
            raise exceptions.UserCredentialsException(
                "Authentication error using token: %s" % admin_token)
        try:
            token = self._set_token_in_cache(user_data)
        except Exception as e:
            raise exceptions.UserCredentialsException("Invalid user information")
        return token

    def remove_token_from_cache(self, token):
        """remove token from token store

        :param token: token looked for
        """
        if token not in self.token_store:
            raise exceptions.UserCredentialsException(
                "Token not found")
        del self.token_store[token]

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
        self.token_store.update({token: current_token})

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
        self.token_store.update({token: current_token})


    def authorize(self, token):
        """Authorize user token for the requested services.

        :param token: token
        """
        token_info = self._get_token_from_cache(token)
        return token_info
