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

import testtools

from bdocker.server.modules import credentials
from bdocker.common import exceptions


def create_parameters():
        parameters = {"token":"tokennnnnn"
                        ,"user_credentials":
                        {'uid': 'uuuuuuuuuuiiiidddddd',
                         'gid': 'gggggggggguuuiiidd'}
                    }
        return parameters


class TestUserCredentials(testtools.TestCase):
    """Test User Credential controller."""

    def setUp(self):
        super(TestUserCredentials, self).setUp()
        self.path = "/home/jorge/Dropbox/INDIGO_DOCKER/" \
                    "bdocker/bdocker/tests/server/fake_token_store.yml"
        self.control = credentials.UserController(self.path)

    def test_token_store(self):
        user_info = self.control._get_token_from_cache("token1")
        self.assertEqual(3, user_info.__len__())

    def test_prolog_token(self):
        user_info = self.control._get_token_from_cache("prolog")
        self.assertEqual(1, user_info.__len__())
        self.assertEqual("token_prolog", user_info['token'])

    def test_authenticate(self):
        t = self.control._get_token_from_cache(
            "prolog")['token']
        u = create_parameters()['user_credentials']
        token = self.control.authenticate(admin_token=t,
                                          user_data=u)
        self.assertIsNotNone(token)

    def test_authenticate_save_file(self):
        t = self.control._get_token_from_cache("prolog")['token']
        u = create_parameters()['user_credentials']
        token = self.control.authenticate(admin_token=t,
                                          user_data=u)
        self.assertIsNotNone(token)
        self.control._save_token_file()
        new_controller = credentials.UserController(self.path)
        user_info1 = new_controller._get_token_from_cache(token)
        self.assertEqual(2, user_info1.__len__())
        new_controller.remove_token_from_cache(token)
        new_controller._save_token_file()
        self.assertRaises(exceptions.UserCredentialsException,
                          new_controller._get_token_from_cache,
                          token)

    def test_authorize(self):
        t = 'token2'
        ath = self.control.authorize(t)
        self.assertIsNotNone(ath)

    def test_authorize_err(self):
        t = 'token'
        self.assertRaises(exceptions.UserCredentialsException,
            self.control.authorize, t)

    def test_authorize_containers(self):
        t = 'token2'
        c = 'cotainer1'
        ath = self.control.authorize_container(
            token=t,
            container_id=c)
        self.assertIs(True, ath)

    def test_authorize_container_err(self):
        t = 'token'
        c = '84848'
        self.assertRaises(exceptions.UserCredentialsException,
            self.control.authorize_container, t, c)

    def test_add_container(self):
        token = "token2"
        c_id = "container3"
        token_info = self.control._get_token_from_cache(token)
        self.assertIsNotNone(token_info['containers'])
        self.assertEqual(2,
                         token_info['containers'].__len__())
        self.control.add_container(token, c_id)
        self.assertIsNotNone(
            token_info['containers'])
        self.assertEqual(3,
                         token_info['containers'].__len__())
        self.control.remove_container(token, c_id)
        self.assertIsNotNone(token_info['containers'])
        self.assertEqual(2,
                         token_info['containers'].__len__())

    def test_create_remove_container(self):
        token = "token1"
        c_id = "container1"
        token_info = self.control._get_token_from_cache(token)
        self.assertNotIn('containers', token_info)
        self.control.add_container(token, c_id)
        self.assertIsNotNone(token_info['containers'])
        self.assertEqual(1,
                         token_info['containers'].__len__())
        self.control.remove_container(token, c_id)
        self.assertNotIn('containers', token_info)