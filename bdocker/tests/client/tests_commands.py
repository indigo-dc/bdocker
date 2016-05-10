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

import mock
import testtools
import uuid


from bdocker.client.controller import commands
from bdocker.client.controller import request
from bdocker.common import exceptions


class TestCommands(testtools.TestCase):
    """Test User Credential controller."""

    def setUp(self):
        super(TestCommands, self).setUp()
        path = ("/home/jorge/Dropbox/INDIGO_DOCKER/bdocker/"
                "bdocker/common/configure_bdocker.cfg")
        self.control = commands.CommandController(path)

    def test_create_command_with_root_file(self):
        self.assertRaises(exceptions.UserCredentialsException,
                          commands.CommandController,
                          '/root/.config')

    def test_create_configuration_error(self):
        err_file = ("/home/jorge/Dropbox/INDIGO_DOCKER/"
                    "bdocker/bdocker/tests/client/"
                    "configure_bdocker_error.cfg")
        self.assertRaises(exceptions.ConfigurationException,
                          commands.CommandController,
                          err_file)

    def test_create_credentials_token_in_root(self):
        err_file = ("/home/jorge/Dropbox/INDIGO_DOCKER/"
                    "bdocker/bdocker/tests/client/"
                    "configure_bdocker_root.cfg")
        root_control = commands.CommandController(err_file)
        self.assertRaises(exceptions.UserCredentialsException,
                          root_control.create_credentials,
                          1)

    @mock.patch.object(request.RequestController, "execute_put")
    @mock.patch("bdocker.client.controller.utils.get_user_credentials")
    @mock.patch("bdocker.client.controller.utils.write_user_credentials")
    def test_create_credentials_no_root(self, m_write, m_u, m_put):
        token = uuid.uuid4().hex
        home_dir = "/foo"
        m_u.return_value = {'uid': "", 'gid': "", 'home': home_dir}
        m_put.return_value = token
        u = self.control.create_credentials(1000)
        self.assertIsNotNone(u)
        self.assertEqual(token, u['token'])
        self.assertIn(home_dir, u['path'])

    @mock.patch.object(request.RequestController, "execute_put")
    def test_container_pull(self, m):
        token = uuid.uuid4().hex
        image_id = uuid.uuid4().hex
        source = "foo"
        m.return_value = image_id
        results = self.control.container_pull(token, source)
        self.assertEqual(image_id, results)

    @mock.patch.object(request.RequestController, "execute_post")
    def test_container_run(self, m):
        token = uuid.uuid4().hex
        image_id = uuid.uuid4().hex
        container_id = uuid.uuid4().hex
        err = None
        m.return_value = container_id
        results = self.control.container_run(token, image_id, False, 'ls')
        self.assertEqual(container_id, results)

    @mock.patch.object(request.RequestController, "execute_post")
    def test_container_run(self, m):
        token = uuid.uuid4().hex
        image_id = uuid.uuid4().hex
        container_id = uuid.uuid4().hex
        out =  ['bin', 'etc', 'lib']
        m.return_value = ['bin', 'etc', 'lib']
        results = self.control.container_run(token, image_id, False, 'ls')
        self.assertEqual(out, results)


    @mock.patch.object(request.RequestController, "execute_get")
    def test_container_list(self, m):
        token = uuid.uuid4().hex
        containers = ["container_1", "container_2"]
        m.return_value = {"results": containers}
        results = self.control.container_list(token)
        self.assertEqual(containers[0], results[0])
        self.assertEqual(containers[1], results[1])


    # def test_crendentials(self):
    #     results = self.control.create_credentials(1000)
    #     self.assertIsNotNone(results)

        # CREATE CONTAINER {'Id': '8a61192da2b3bb2d922875585e29b74ec0dc4e0117fcbf84c962204e97564cd7', 'Warnings': None}
