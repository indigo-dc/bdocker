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
        self.control = commands.CommandController()

    def test_create_credentials_root(self):
        self.assertRaises(exceptions.UserCredentialsException,
                          commands.CommandController,
                          '/root/.config')

    def test_create_credentials_error(self):
        err_file = ("/home/jorge/Dropbox/INDIGO_DOCKER/"
                    "bdocker/bdocker/tests/client/"
                    "configure_bdocker_error.cfg")
        self.assertRaises(exceptions.ConfigurationException,
                          commands.CommandController,
                          err_file)

    @mock.patch.object(request.RequestController, "execute_put")
    def test_create_credentials_no_root(self, m):
        m.return_value = uuid.uuid4().hex
        u = self.control.create_credentials(1000)
        self.assertIsNotNone(u)

    @mock.patch.object(request.RequestController, "execute_put")
    def test_container_pull(self, m):
        token = uuid.uuid4().hex
        image_id = uuid.uuid4().hex
        source = "foo"
        m.return_value = image_id
        u = self.control.container_pull(token, source)
        self.assertIsNotNone(u)
