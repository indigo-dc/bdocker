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
import webob


from bdocker.server import docker
from bdocker.server.modules import credentials
from bdocker.server import restful_api
from bdocker.tests import server

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


class TestREST(server.TestConfiguration):
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


    @mock.patch.object(docker.DockerController, "pull_image")
    @mock.patch.object(credentials.UserController,
                   "authorize")
    @mock.patch.object(credentials.UserController,
                   "add_container")
    def test_pull(self, mc, mu, md):
        mu.return_value=True
        parameters = {"token":"tokennnnnn",
                      "repo": 'repoooo'}
        body = make_body(parameters)
        result = webob.Request.blank("/pull",
                                     content_type="application/json",
                                     body=body,
                                     method="PUT").get_response(self.app)
        self.assertEqual(201, result.status_code)

    @mock.patch.object(docker.DockerController, "pull_image")
    def test_pull_405(self, m):
        parameters = {"token":"tokennnnnn",
                      "repo": 'repoooo'}
        body = make_body(parameters)
        result = webob.Request.blank("/pull",
                                     content_type="application/json",
                                     body=body,
                                     method="GET").get_response(self.app)
        self.assertEqual(405, result.status_code)

    @mock.patch.object(docker.DockerController, "pull_image")
    def test_pull_400(self, m):
        parameters = {"token":"tokennnnnn"}
        body = make_body(parameters)
        result = webob.Request.blank("/pull",
                                     content_type="application/json",
                                     body=body,
                                     method="put").get_response(self.app)
        self.assertEqual(400, result.status_code)

    @mock.patch.object(docker.DockerController, "delete_container")
    @mock.patch.object(credentials.UserController,
                       "authorize_container")
    def test_delete(self, mu, md):
        mu.return_value = True
        parameters = {"token":"tokennnnnn",
                      "container_id": 'repoooo'}
        query = get_query_string(parameters)
        result = webob.Request.blank("/rm?%s" % query,
                                     method="DELETE").get_response(self.app)
        self.assertEqual(204, result.status_code)

    @mock.patch.object(docker.DockerController, "delete_container")
    def test_delete_405(self, m):
        parameters = {"token":"tokennnnnn",
                      "container_id": 'repoooo'}
        query = get_query_string(parameters)
        result = webob.Request.blank("/rm?%s" % query,
                                     method="GET").get_response(self.app)
        self.assertEqual(405, result.status_code)

    @mock.patch.object(docker.DockerController, "delete_container")
    def test_delete(self, mu):
        mu.return_value = True
        parameters = {"token":"tokennnnnn",
                      "container_id": 'repoooo'}
        query = get_query_string(parameters)
        result = webob.Request.blank("/rm?%s" % query,
                                     method="DELETE").get_response(self.app)
        self.assertEqual(401, result.status_code)

    @mock.patch.object(docker.DockerController, "list_containers")
    @mock.patch.object(credentials.UserController, "list_containers")
    @mock.patch.object(credentials.UserController,
                       "authorize")
    def test_ps(self, mu, md,ml):
        mu.return_value = True
        result = webob.Request.blank("/ps?token=333333",
                                     method="GET").get_response(self.app)
        self.assertEqual(200, result.status_code)

    @mock.patch.object(docker.DockerController, "list_containers")
    def test_ps_401(self, m):
        result = webob.Request.blank("/ps?token=333333",
                                     method="GET").get_response(self.app)
        self.assertEqual(401, result.status_code)

    @mock.patch.object(docker.DockerController, "list_containers")
    def test_ps_405(self, m):
        result = webob.Request.blank("/ps?token=333333",
                                     method="PUT").get_response(self.app)
        self.assertEqual(405, result.status_code)

    @mock.patch.object(docker.DockerController, "logs_container")
    @mock.patch.object(credentials.UserController,
                       "authorize_container")
    def test_logs(self, mu, md):
        mu.return_value = True
        parameters = {"token":"tokennnnnn",
                      "container_id": 'containerrrrr'}
        query = get_query_string(parameters)
        result = webob.Request.blank("/logs?%s" % query,
                                     method="GET").get_response(self.app)
        self.assertEqual(200, result.status_code)

    @mock.patch.object(docker.DockerController, "logs_container")
    def test_logs_401(self, m):
        parameters = {"token":"tokennnnnn",
                      "container_id": 'containerrrrr'}
        query = get_query_string(parameters)
        result = webob.Request.blank("/logs?%s" % query,
                                     method="GET").get_response(self.app)
        self.assertEqual(401, result.status_code)

    @mock.patch.object(docker.DockerController, "logs_container")
    def test_logs_405(self, m):
        parameters = {"token":"tokennnnnn",
                      "container_id": 'containerrrrr'}
        query = get_query_string(parameters)
        result = webob.Request.blank("/logs?%s" % query,
                                     method="POST").get_response(self.app)
        self.assertEqual(405, result.status_code)

    # @mock.patch.object(docker.DockerController, "start_container")
    # @mock.patch.object(credentials.UserController,
    #                    "authorize_container")
    # def test_start(self, mu, md):
    #     mu.return_value = True
    #     parameters = {"token":"tokennnnnn",
    #                   "container_id": 'containerrrrr'}
    #     body = make_body(parameters)
    #     result = webob.Request.blank("/start",
    #                                  content_type="application/json",
    #                                  body=body,
    #                                  method="POST").get_response(self.app)
    #     self.assertEqual(201, result.status_code)
    #
    # @mock.patch.object(docker.DockerController, "start_container")
    # def test_start_405(self, md):
    #     parameters = {"token":"tokennnnnn",
    #                   "container_id": 'containerrrrr'}
    #     body = make_body(parameters)
    #     result = webob.Request.blank("/start",
    #                                  content_type="application/json",
    #                                  body=body,
    #                                  method="GET").get_response(self.app)
    #     self.assertEqual(405, result.status_code)
    #
    # @mock.patch.object(docker.DockerController, "start_container")
    # def test_start_401(self, m):
    #     parameters = {"token":"tokennnnnn",
    #                   "container_id": 'containerrrrr'}
    #     body = make_body(parameters)
    #     result = webob.Request.blank("/start",
    #                                  content_type="application/json",
    #                                  body=body,
    #                                  method="POST").get_response(self.app)
    #     self.assertEqual(401, result.status_code)

    @mock.patch.object(docker.DockerController, "stop_container")
    @mock.patch.object(credentials.UserController,
                       "authorize_container")
    def test_stop(self, mu, md):
        mu.return_value = True
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

    @mock.patch.object(docker.DockerController, "stop_container")
    def test_stop_401(self, m):
        parameters = {"token":"tokennnnnn",
                      "container_id": 'containerrrrr'}
        body = make_body(parameters)
        result = webob.Request.blank("/stop",
                                     content_type="application/json",
                                     body=body,
                                     method="POST").get_response(self.app)
        self.assertEqual(401, result.status_code)

    @mock.patch.object(docker.DockerController, "run_container")
    @mock.patch.object(credentials.UserController,
                       "add_container")
    def test_run(self, mu, md):
        mu.return_value = True
        md.return_value = {'Id':'33333'}
        parameters = {"token":"tokennnnnn",
                      "image_id": 'containerrrrr',
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
                      "image_id": 'containerrrrr',
                      "script": "scriptttt"}
        body = make_body(parameters)
        result = webob.Request.blank("/run",
                                     content_type="application/json",
                                     body=body,
                                     method="GET").get_response(self.app)
        self.assertEqual(405, result.status_code)

    @mock.patch.object(docker.DockerController, "run_container")
    def test_run_401(self, m):
        parameters = {"token":"tokennnnnn",
                      "image_id": 'containerrrrr',
                      "script": "scriptttt"}
        body = make_body(parameters)
        result = webob.Request.blank("/run",
                                     content_type="application/json",
                                     body=body,
                                     method="POST").get_response(self.app)
        self.assertEqual(401, result.status_code)

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
    @mock.patch.object(credentials.UserController,
                       "authorize")
    def test_acc(self, mu, md):
        mu.return_value = True
        parameters = {"token":"tokennnnnn",
                      "container_id": 'containerrrrr'}
        query = get_query_string(parameters)
        result = webob.Request.blank("/accounting?%s" % query,
                                     method="GET").get_response(self.app)
        self.assertEqual(200, result.status_code)

    @mock.patch.object(docker.DockerController, "accounting_container")
    def test_acc_401(self, m):
        parameters = {"token":"tokennnnnn",
                      "container_id": 'containerrrrr'}
        query = get_query_string(parameters)
        result = webob.Request.blank("/accounting?%s" % query,
                                     method="GET").get_response(self.app)
        self.assertEqual(401, result.status_code)

    @mock.patch.object(docker.DockerController, "accounting_container")
    def test_acc_401(self, m):
        parameters = {"token":"tokennnnnn",
                      "container_id": 'containerrrrr'}
        query = get_query_string(parameters)
        result = webob.Request.blank("/accounting?%s" % query,
                                     method="GET").get_response(self.app)
        self.assertEqual(401, result.status_code)

    @mock.patch.object(docker.DockerController, "accounting_container")
    def test_acc_405(self, m):
        parameters = {"token":"tokennnnnn",
                      "container_id": 'containerrrrr'}
        query = get_query_string(parameters)
        result = webob.Request.blank("/accounting?%s" % query,
                                     method="POST").get_response(self.app)
        self.assertEqual(405, result.status_code)

    @mock.patch.object(docker.DockerController, "output_task")
    @mock.patch.object(credentials.UserController,
                       "authorize_container")
    def test_output(self, mu, md):
        mu.return_value = True
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

    @mock.patch.object(docker.DockerController, "output_task")
    def test_output_401(self, m):
        parameters = {"token":"tokennnnnn",
                      "container_id": 'containerrrrr'}
        query = get_query_string(parameters)
        result = webob.Request.blank("/output?%s" % query,
                                     method="GET").get_response(self.app)
        self.assertEqual(401, result.status_code)
