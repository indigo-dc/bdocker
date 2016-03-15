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
import webob

from bdocker.server import docker
from bdocker.server import restful_api

# todo(jorgesece): test results retrieve


class TestREST(testtools.TestCase):
    """Test OCCI compute controller."""

    def setUp(self):
        super(TestREST, self).setUp()
        self.app = restful_api.app

    @mock.patch.object(docker.DockerController, "pull_container")
    def test_pull(self, m):
        result = webob.Request.blank("/pull",
                                     method="PUT").get_response(self.app)
        self.assertEqual(201, result.status_code)

    @mock.patch.object(docker.DockerController, "pull_container")
    def test_pul_405l(self, m):
        #m.return_value = {}
        result = webob.Request.blank("/pull",
                                     method="GET").get_response(self.app)
        self.assertEqual(405, result.status_code)

    @mock.patch.object(docker.DockerController, "delete_container")
    def test_delete(self, m):
        result = webob.Request.blank("/delete",
                                     method="DELETE").get_response(self.app)
        self.assertEqual(204, result.status_code)

    @mock.patch.object(docker.DockerController, "delete_container")
    def test_delete_405(self, m):
        result = webob.Request.blank("/delete",
                                     method="GET").get_response(self.app)
        self.assertEqual(405, result.status_code)

    @mock.patch.object(docker.DockerController, "list_container")
    def test_ps(self, m):
        result = webob.Request.blank("/ps",
                                     method="GET").get_response(self.app)
        self.assertEqual(200, result.status_code)

    @mock.patch.object(docker.DockerController, "list_container")
    def test_ps_405(self, m):
        result = webob.Request.blank("/ps",
                                     method="PUT").get_response(self.app)
        self.assertEqual(405, result.status_code)

    @mock.patch.object(docker.DockerController, "logs_container")
    def test_logs(self, m):
        result = webob.Request.blank("/logs",
                                     method="GET").get_response(self.app)
        self.assertEqual(200, result.status_code)

    @mock.patch.object(docker.DockerController, "logs_container")
    def test_logs_405(self, m):
        result = webob.Request.blank("/logs",
                                     method="POST").get_response(self.app)
        self.assertEqual(405, result.status_code)

    @mock.patch.object(docker.DockerController, "start_container")
    def test_start(self, m):
        result = webob.Request.blank("/start",
                                     method="POST").get_response(self.app)
        self.assertEqual(201, result.status_code)

    @mock.patch.object(docker.DockerController, "start_container")
    def test_start_405(self, m):
        result = webob.Request.blank("/start",
                                     method="GET").get_response(self.app)
        self.assertEqual(405, result.status_code)

    @mock.patch.object(docker.DockerController, "stop_container")
    def test_stop(self, m):
        result = webob.Request.blank("/stop",
                                     method="POST").get_response(self.app)
        self.assertEqual(200, result.status_code)

    @mock.patch.object(docker.DockerController, "stop_container")
    def test_stop_405(self, m):
        result = webob.Request.blank("/stop",
                                     method="GET").get_response(self.app)
        self.assertEqual(405, result.status_code)

    @mock.patch.object(docker.DockerController, "run_container")
    def test_run(self, m):
        result = webob.Request.blank("/run",
                                     method="POST").get_response(self.app)
        self.assertEqual(201, result.status_code)

    @mock.patch.object(docker.DockerController, "run_container")
    def test_run_405(self, m):
        result = webob.Request.blank("/run",
                                     method="GET").get_response(self.app)
        self.assertEqual(405, result.status_code)

    @mock.patch.object(docker.DockerController, "accounting_container")
    def test_acc(self, m):
        result = webob.Request.blank("/accounting",
                                     method="GET").get_response(self.app)
        self.assertEqual(200, result.status_code)

    @mock.patch.object(docker.DockerController, "accounting_container")
    def test_acc_405(self, m):
        result = webob.Request.blank("/accounting",
                                     method="POST").get_response(self.app)
        self.assertEqual(405, result.status_code)

    @mock.patch.object(docker.DockerController, "output_task")
    def test_output(self, m):
        result = webob.Request.blank("/output",
                                     method="GET").get_response(self.app)
        self.assertEqual(200, result.status_code)

    @mock.patch.object(docker.DockerController, "output_task")
    def test_output_405(self, m):
        result = webob.Request.blank("/output",
                                     method="POST").get_response(self.app)
        self.assertEqual(405, result.status_code)