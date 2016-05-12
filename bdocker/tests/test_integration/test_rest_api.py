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
import os
import testtools
import webob

os.environ['BDOCKER_CONF_FILE'] = "/home/jorge/Dropbox/INDIGO_DOCKER/bdocker/bdocker/common/configure_bdocker.cfg"

from bdocker.server import restful_api


class TestIntegration(testtools.TestCase):
    def setUp(self):
        super(TestIntegration, self).setUp()
        self.app = restful_api.app

    def create_request(self, path="/",
                       **kwargs):
        return webob.Request.blank(path=path, **kwargs)

class TestRESTIntegration(TestIntegration):
    """Test REST request mapping."""

    def setUp(self):
        super(TestRESTIntegration, self).setUp()

    def test_ps_real(self,):

        token = "1866e0ca1ad44a55952029817c2a5345"
        all = False
        path = "/ps?token=%s&all=%s" % (token, all)
        req = self.create_request(path, method="GET")
        result = req.get_response(self.app)

        self.assertEqual(200, result.status_code)
        self.assertEqual([], result.json_body['results'])

    def test_ps_real_all(self):

        token = "1866e0ca1ad44a55952029817c2a5345"
        all = True
        path = "/ps?token=%s&all=%s" % (token, all)
        req = self.create_request(path, method="GET")
        result = req.get_response(self.app)

        self.assertEqual(200, result.status_code)
        self.assertIsNot([], result.json_body['results'])