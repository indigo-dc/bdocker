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

import json
import mock
import testtools
import webob


from bdocker.common import request


def create_fake_json_resp(data, status=200):
    r = webob.Response()
    r.headers["Content-Type"] = "application/json"
    r.charset = "utf8"
    r.body = json.dumps(data).encode("utf8")
    r.status_code = status
    return r


class TestRequest(testtools.TestCase):
    """Test User Credential controller."""

    def setUp(self):
        super(TestRequest, self).setUp()
        self.control = request.RequestController()

    @mock.patch.object(webob.Request, "get_response")
    def test_PUT(self, m):
        t = "tokenResult"
        fake_response = webob.Response()
        fake_response.status_int = 201
        fake_response.body = '{"results": "%s", "status_code": 201}' % t
        m.return_value = fake_response
        parameters = {"token":"tokennnnnn",
                      "user_credentials": {
                          'uid': 'uuuuuuuuuuiiiidddddd',
                          'gid': 'gggggggggguuuiiidd'}
                      }
        path = "/credentials"
        result = self.control.execute_put(path=path, parameters=parameters)
        self.assertEqual(t, result)

    @mock.patch.object(webob.Request, "get_response")
    def test_GET(self, m):
        r = ['cont1', 'cont2', 'cont3']
        fake_response = create_fake_json_resp({'results': r
                                               }, 200)
        m.return_value = fake_response
        parameters = {"token":"tokennnnnn"}
        path = "/ps?token"
        result = self.control.execute_get(path=path, parameters=parameters)
        self.assertEqual(r, result)

    @mock.patch.object(webob.Request, "get_response")
    def test_GET_500(self, m):
        fake_response = create_fake_json_resp({}, 500)
        m.return_value = fake_response
        parameters = {"token":"tokennnnnn"}
        path = "/ps?token"
        self.assertRaises(webob.exc.HTTPInternalServerError,
                          self.control.execute_get,
                          path=path, parameters=parameters)