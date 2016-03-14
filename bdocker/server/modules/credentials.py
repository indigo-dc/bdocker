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

from bdocker import exceptions
from bdocker.server.modules import utils


class UserController(object):

    def __init__(self, path):
        self.token_store = utils.load_from_yaml_file(path)

    def _get_token_from_cache(self, token):
        if token not in self.token_store:
            raise exceptions.UserCredentialsException(
                "Token not found")
        return self.token_store[token]

    def _set_token_in_cache(self, user_info):
        token = uuid.uuid4().hex
        new_token = {token: {
                            'uid': user_info['uid'],
                            'guid': user_info['guid'],
                            }
                    }
        self.token_store.update(new_token)
        return token

    def _update_token_in_cache(self, token, others):
        current_token = self._get_token_from_cache(token)
        for key,value in others.items():
            current_token[key] = value
        self.token_store.update({token: current_token})

    def authenticate(self, user_data):
        # todo(jorgesece): valid user?
        #if not user_data:
        #    return False
        token = self._set_token_in_cache(user_data)
        return token

    def authorizate(self, token, policies):
        token_info = self._get_token_from_cache(token)
        # todo(jorgesece): token_info['uid'] is ok
        return token_info

    def validate_admin(self):
        pass