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
import mock

from bdocker.client.controller import commands
from bdocker.client.controller import request

class TestCommands(testtools.TestCase):
    """Test User Credential controller."""

    def setUp(self):
        super(TestCommands, self).setUp()
        self.control = commands.CommandController()

    @mock.patch.object(request.RequestController, "execute_put")
    def test_create_credentials(self, m):
        m.return_value = 'Tokennnnnnnnnnnnn'
        u = self.control.create_credentials(1000)
        self.assertIsNotNone(u)