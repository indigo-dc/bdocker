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


from bdocker.server import docker
from bdocker.server.modules import credentials
from bdocker.server import restful_api

# todo(jorgesece): test results retrieve


def make_body(parameters):
        body = {}
        for key in parameters.keys():
            body[key] = parameters[key]

        return json.dumps(body)


def get_query_string(parameters):
        query_string = ""
        if parameters is None:
            return None

        for key in parameters.keys():
            query_string = ("%s%s=%s&" % (query_string, key, parameters[key]))

        return query_string[:-1] # delete last character


class TestREST(testtools.TestCase):
    """Test REST request mapping."""

    def setUp(self):
        super(TestREST, self).setUp()
        self.app = restful_api.app

    @mock.patch.object(credentials.UserController, "authenticate")
    def test_credentials(self, m):
        m.return_value = 'tokenresult'
        parameters = {"token": "tokennnnnn",
                      "user_credentials":
                          {'uid': 'uuuuuuuuuuiiiidddddd',
                           'gid': 'gggggggggguuuiiidd'}
                      }
        body = make_body(parameters)
        result = webob.Request.blank("/credentials",
                                     method="PUT",
                                     content_type="application/json",
                                     body=body).get_response(self.app)
        self.assertEqual(201, result.status_code)


    @mock.patch.object(docker.DockerController, "pull_container")
    def test_pull(self, m):
        parameters = {"token":"tokennnnnn",
                      "repo": 'repoooo'}
        body = make_body(parameters)
        result = webob.Request.blank("/pull",
                                     content_type="application/json",
                                     body=body,
                                     method="PUT").get_response(self.app)
        self.assertEqual(201, result.status_code)

    @mock.patch.object(docker.DockerController, "pull_container")
    def test_pull_405(self, m):
        parameters = {"token":"tokennnnnn",
                      "repo": 'repoooo'}
        body = make_body(parameters)
        result = webob.Request.blank("/pull",
                                     content_type="application/json",
                                     body=body,
                                     method="GET").get_response(self.app)
        self.assertEqual(405, result.status_code)

    @mock.patch.object(docker.DockerController, "pull_container")
    def test_pull_400(self, m):
        parameters = {"token":"tokennnnnn"}
        body = make_body(parameters)
        result = webob.Request.blank("/pull",
                                     content_type="application/json",
                                     body=body,
                                     method="put").get_response(self.app)
        self.assertEqual(400, result.status_code)

    @mock.patch.object(docker.DockerController, "delete_container")
    def test_delete(self, m):
        parameters = {"token":"tokennnnnn",
                      "container_id": 'repoooo'}
        query = get_query_string(parameters)
        result = webob.Request.blank("/delete?%s" % query,
                                     method="DELETE").get_response(self.app)
        self.assertEqual(204, result.status_code)

    @mock.patch.object(docker.DockerController, "delete_container")
    def test_delete_405(self, m):
        parameters = {"token":"tokennnnnn",
                      "container_id": 'repoooo'}
        query = get_query_string(parameters)
        result = webob.Request.blank("/delete?%s" % query,
                                     method="GET").get_response(self.app)
        self.assertEqual(405, result.status_code)

    @mock.patch.object(docker.DockerController, "list_container")
    def test_ps(self, m):
        result = webob.Request.blank("/ps?token=333333",
                                     method="GET").get_response(self.app)
        self.assertEqual(200, result.status_code)

    @mock.patch.object(docker.DockerController, "list_container")
    def test_ps_405(self, m):
        result = webob.Request.blank("/ps?token=333333",
                                     method="PUT").get_response(self.app)
        self.assertEqual(405, result.status_code)

    @mock.patch.object(docker.DockerController, "logs_container")
    def test_logs(self, m):
        parameters = {"token":"tokennnnnn",
                      "container_id": 'containerrrrr'}
        query = get_query_string(parameters)
        result = webob.Request.blank("/logs?%s" % query,
                                     method="GET").get_response(self.app)
        self.assertEqual(200, result.status_code)

    @mock.patch.object(docker.DockerController, "logs_container")
    def test_logs_405(self, m):
        parameters = {"token":"tokennnnnn",
                      "container_id": 'containerrrrr'}
        query = get_query_string(parameters)
        result = webob.Request.blank("/logs?%s" % query,
                                     method="POST").get_response(self.app)
        self.assertEqual(405, result.status_code)

    @mock.patch.object(docker.DockerController, "start_container")
    def test_start(self, m):
        parameters = {"token":"tokennnnnn",
                      "container_id": 'containerrrrr'}
        body = make_body(parameters)
        result = webob.Request.blank("/start",
                                     content_type="application/json",
                                     body=body,
                                     method="POST").get_response(self.app)
        self.assertEqual(201, result.status_code)

    @mock.patch.object(docker.DockerController, "start_container")
    def test_start_405(self, m):
        parameters = {"token":"tokennnnnn",
                      "container_id": 'containerrrrr'}
        body = make_body(parameters)
        result = webob.Request.blank("/start",
                                     content_type="application/json",
                                     body=body,
                                     method="GET").get_response(self.app)
        self.assertEqual(405, result.status_code)

    @mock.patch.object(docker.DockerController, "stop_container")
    def test_stop(self, m):
        parameters = {"token":"tokennnnnn",
                      "container_id": 'containerrrrr'}
        body = make_body(parameters)
        result = webob.Request.blank("/stop",
                                     content_type="application/json",
                                     body=body,
                                     method="POST").get_response(self.app)
        self.assertEqual(200, result.status_code)

    @mock.patch.object(docker.DockerController, "stop_container")
    def test_stop_405(self, m):
        parameters = {"token":"tokennnnnn",
                      "container_id": 'containerrrrr'}
        body = make_body(parameters)
        result = webob.Request.blank("/stop",
                                     content_type="application/json",
                                     body=body,
                                     method="GET").get_response(self.app)
        self.assertEqual(405, result.status_code)

    @mock.patch.object(docker.DockerController, "run_container")
    def test_run(self, m):
        parameters = {"token":"tokennnnnn",
                      "container_id": 'containerrrrr',
                      "script": "scriptttt"}
        body = make_body(parameters)
        result = webob.Request.blank("/run",
                                     content_type="application/json",
                                     body=body,
                                     method="POST").get_response(self.app)
        self.assertEqual(201, result.status_code)

    @mock.patch.object(docker.DockerController, "run_container")
    def test_run_405(self, m):
        parameters = {"token":"tokennnnnn",
                      "container_id": 'containerrrrr',
                      "script": "scriptttt"}
        body = make_body(parameters)
        result = webob.Request.blank("/run",
                                     content_type="application/json",
                                     body=body,
                                     method="GET").get_response(self.app)
        self.assertEqual(405, result.status_code)

    @mock.patch.object(docker.DockerController, "run_container")
    def test_run_400(self, m):
        parameters = {"token":"tokennnnnn",
                      "script": "scriptttt"}
        body = make_body(parameters)
        result = webob.Request.blank("/run",
                                     content_type="application/json",
                                     body=body,
                                     method="POST").get_response(self.app)
        self.assertEqual(400, result.status_code)

    @mock.patch.object(docker.DockerController, "accounting_container")
    def test_acc(self, m):
        parameters = {"token":"tokennnnnn",
                      "container_id": 'containerrrrr'}
        query = get_query_string(parameters)
        result = webob.Request.blank("/accounting?%s" % query,
                                     method="GET").get_response(self.app)
        self.assertEqual(200, result.status_code)

    @mock.patch.object(docker.DockerController, "accounting_container")
    def test_acc_405(self, m):
        parameters = {"token":"tokennnnnn",
                      "container_id": 'containerrrrr'}
        query = get_query_string(parameters)
        result = webob.Request.blank("/accounting?%s" % query,
                                     method="POST").get_response(self.app)
        self.assertEqual(405, result.status_code)

    @mock.patch.object(docker.DockerController, "output_task")
    def test_output(self, m):
        parameters = {"token":"tokennnnnn",
                      "container_id": 'containerrrrr'}
        query = get_query_string(parameters)
        result = webob.Request.blank("/output?%s" % query,
                                     method="GET").get_response(self.app)
        self.assertEqual(200, result.status_code)

    @mock.patch.object(docker.DockerController, "output_task")
    def test_output_405(self, m):
        parameters = {"token":"tokennnnnn",
                      "container_id": 'containerrrrr'}
        query = get_query_string(parameters)
        result = webob.Request.blank("/output?%s" % query,
                                     method="POST").get_response(self.app)
        self.assertEqual(405, result.status_code)
