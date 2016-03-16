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
import webob


from bdocker.client.controller import request
from bdocker.server import utils


class TestCommands(testtools.TestCase):
    """Test User Credential controller."""

    def setUp(self):
        super(TestCommands, self).setUp()
        self.control = request.RequestController()

    @mock.patch.object(webob.Request, "get_response")
    def test_PUT(self, m):
        t = "tokenResult"
        fake_response = webob.Response()
        fake_response.status_int = 201
        fake_response.body = '{"results": "%s", "status_code": 201}' % t
        m.return_value = fake_response
        parameters = {"token":"tokennnnnn"
                        ,"user_credentials":
                        {'uid': 'uuuuuuuuuuiiiidddddd',
                         'gid': 'gggggggggguuuiiidd'}
                    }
        path = "/credentials"
        result = self.control.execute_put(path=path, parameters=parameters)
        self.assertEqual(t, result)

    @mock.patch.object(webob.Request, "get_response")
    def test_GET(self, m):
        r = "[cont1, cont2, cont3]"
        fake_response = webob.Response()
        fake_response.status_int = 200
        fake_response.body = '{"results": "%s", "status_code": 201}' % r
        m.return_value = fake_response
        parameters = {"token":"tokennnnnn"}
        path = "/ps"
        result = self.control.execute_get(path=path, parameters=parameters)
        self.assertEqual(r, result)