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
import os
import uuid
import webob

import mock

os.environ['BDOCKER_CONF_FILE'] = "/home/jorge/Dropbox/INDIGO_DOCKER/bdocker/bdocker/common/configure_bdocker.cfg"

from bdocker.client.controller import utils
from bdocker.common.modules import credentials
from bdocker.common.modules import docker_helper
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
                           'gid': 'gggggggggguuuiiidd',
                           'job': {'id':'gggggggggguuuiiidd',
                                   'spool':'/faa'}
                           }
                      }
        body = make_body(parameters)
        result = webob.Request.blank("/credentials",
                                     method="POST",
                                     content_type="application/json",
                                     body=body).get_response(self.app)
        self.assertEqual(201, result.status_code)


    @mock.patch.object(docker_helper.DockerController, "pull_image")
    @mock.patch.object(credentials.UserController,
                   "authorize")
    @mock.patch.object(credentials.UserController,
                   "add_image")
    def test_pull(self, mc, mu, md):
        im_id = 'X'
        mu.return_value = True
        md.return_value = {'image_id': im_id, 'status':'OK'}
        parameters = {"token":"tokennnnnn",
                      "source": 'repoooo'}
        body = make_body(parameters)
        result = webob.Request.blank("/pull",
                                     content_type="application/json",
                                     body=body,
                                     method="POST").get_response(self.app)
        self.assertEqual(201, result.status_code)

    @mock.patch.object(docker_helper.DockerController, "pull_image")
    def test_pull_405(self, m):
        parameters = {"token":"tokennnnnn",
                      "source": 'repoooo'}
        body = make_body(parameters)
        result = webob.Request.blank("/pull",
                                     content_type="application/json",
                                     body=body,
                                     method="PUT").get_response(self.app)
        self.assertEqual(405, result.status_code)

    @mock.patch.object(docker_helper.DockerController, "pull_image")
    def test_pull_400(self, m):
        parameters = {"token":"tokennnnnn"}
        body = make_body(parameters)
        result = webob.Request.blank("/pull",
                                     content_type="application/json",
                                     body=body,
                                     method="POST").get_response(self.app)
        self.assertEqual(400, result.status_code)

    @mock.patch.object(docker_helper.DockerController, "delete_container")
    @mock.patch.object(credentials.UserController,
                       "authorize_container")
    @mock.patch.object(credentials.UserController,
                       "remove_container")
    def test_delete(self, mr, mu, md):
        mr.return_value = True
        mu.return_value = True
        parameters = {"token":"tokennnnnn",
                      "container_id": 'repoooo'}
        body = make_body(parameters)
        result = webob.Request.blank("/rm",
                                     content_type="application/json",
                                     body=body,
                                     method="PUT").get_response(self.app)
        self.assertEqual(200, result.status_code)

    @mock.patch.object(docker_helper.DockerController, "delete_container")
    @mock.patch.object(credentials.UserController,
                       "authorize_container")
    @mock.patch.object(credentials.UserController,
                       "remove_container")
    def test_delete_several(self, mr, mu, md):
        c1 = uuid.uuid4().hex
        c2 = uuid.uuid4().hex
        mr.return_value = True
        mu.side_effect = [c1, c2]
        parameters = {"token":"tokennnnnn",
                      "container_id": [c1, c2]}
        body = make_body(parameters)
        result = webob.Request.blank("/rm",
                                     content_type="application/json",
                                     body=body,
                                     method="PUT").get_response(self.app)
        self.assertEqual(200, result.status_code)
        self.assertEqual(c1, result.json_body["results"][0])
        self.assertEqual(c2, result.json_body["results"][1])

    @mock.patch.object(docker_helper.DockerController, "delete_container")
    def test_delete_405(self, m):
        parameters = {"token":"tokennnnnn",
                      "container_id": 'repoooo'}
        query = get_query_string(parameters)
        result = webob.Request.blank("/rm?%s" % query,
                                     method="GET").get_response(self.app)
        self.assertEqual(405, result.status_code)

    @mock.patch.object(docker_helper.DockerController, "delete_container")
    @mock.patch.object(credentials.UserController, "_get_token_from_cache")
    def test_delete_401(self, m_t, mu):
        m_t.return_value = {'containers':['c1']}
        c1 = uuid.uuid4().hex
        c2 = uuid.uuid4().hex
        mu.side_effect = [c1, c2]
        parameters = {"token":"tokennnnnn",
                      "container_id": [c1, c2]}
        body = make_body(parameters)
        result = webob.Request.blank("/rm",
                                     content_type="application/json",
                                     body=body,
                                     method="PUT").get_response(self.app)
        self.assertEqual(200, result.status_code)
        self.assertIn("Error", result.json_body["results"][0])

    @mock.patch.object(docker_helper.DockerController, "list_containers")
    @mock.patch.object(credentials.UserController, "_get_token_from_cache")
    @mock.patch.object(credentials.UserController,
                       "authorize")

    def test_ps(self, mu, mt, ml):
        mu.return_value = True
        token = "3333"
        all = True
        mt.return_value = {"token": token, "containers": ["A", "B"]}
        result = webob.Request.blank("/ps?token=%s&%s" % (token ,all),
                                     method="GET").get_response(self.app)
        self.assertEqual(200, result.status_code)

    @mock.patch.object(docker_helper.DockerController, "list_containers")
    def test_ps_401(self, m):
        result = webob.Request.blank("/ps?token=333333",
                                     method="GET").get_response(self.app)
        self.assertEqual(401, result.status_code)

    @mock.patch.object(docker_helper.DockerController, "list_containers")
    def test_ps_405(self, m):
        result = webob.Request.blank("/ps?token=333333",
                                     method="PUT").get_response(self.app)
        self.assertEqual(405, result.status_code)

    @mock.patch.object(docker_helper.DockerController, "logs_container")
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

    @mock.patch.object(docker_helper.DockerController, "logs_container")
    def test_logs_401(self, m):
        parameters = {"token":"tokennnnnn",
                      "container_id": 'containerrrrr'}
        query = get_query_string(parameters)
        result = webob.Request.blank("/logs?%s" % query,
                                     method="GET").get_response(self.app)
        self.assertEqual(401, result.status_code)

    @mock.patch.object(docker_helper.DockerController, "logs_container")
    def test_logs_405(self, m):
        parameters = {"token":"tokennnnnn",
                      "container_id": 'containerrrrr'}
        query = get_query_string(parameters)
        result = webob.Request.blank("/logs?%s" % query,
                                     method="POST").get_response(self.app)
        self.assertEqual(405, result.status_code)

    @mock.patch.object(docker_helper.DockerController, "stop_container")
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

    @mock.patch.object(docker_helper.DockerController, "stop_container")
    def test_stop_405(self, m):
        parameters = {"token":"tokennnnnn",
                      "container_id": 'containerrrrr'}
        body = make_body(parameters)
        result = webob.Request.blank("/stop",
                                     content_type="application/json",
                                     body=body,
                                     method="GET").get_response(self.app)
        self.assertEqual(405, result.status_code)

    @mock.patch.object(docker_helper.DockerController, "stop_container")
    def test_stop_401(self, m):
        parameters = {"token":"tokennnnnn",
                      "container_id": 'containerrrrr'}
        body = make_body(parameters)
        result = webob.Request.blank("/stop",
                                     content_type="application/json",
                                     body=body,
                                     method="POST").get_response(self.app)
        self.assertEqual(401, result.status_code)

    @mock.patch.object(docker_helper.DockerController, "run_container")
    @mock.patch.object(credentials.UserController,
                   "authorize_image")
    @mock.patch.object(credentials.UserController,
                       "add_container")
    @mock.patch.object(docker_helper.DockerController,
                       "start_container")
    @mock.patch.object(docker_helper.DockerController,
                       "logs_container")
    def test_run(self, m_log, m_start, madd, math, md):
        token = uuid.uuid4().hex
        image_id = uuid.uuid4().hex
        container_id = uuid.uuid4().hex
        script = 'ls'
        detach = False
        madd.return_value = True
        math.return_value = True
        md.return_value = {'Id': container_id}
        parameters = {"token": token,
                      "image_id": image_id,
                      "script": script,
                      "detach": detach
                      }
        body = make_body(parameters)
        result = webob.Request.blank("/run",
                                     content_type="application/json",
                                     body=body,
                                     method="PUT").get_response(self.app)
        self.assertEqual(201, result.status_code)
        # todo: parse to get id

    @mock.patch.object(docker_helper.DockerController, "run_container")
    @mock.patch.object(credentials.UserController,
                   "authorize_image")
    @mock.patch.object(credentials.UserController,
                       "add_container")
    @mock.patch.object(docker_helper.DockerController,
                       "start_container")
    @mock.patch.object(docker_helper.DockerController,
                       "logs_container")
    def test_run_405(self, m_log, m_start, madd, math, md):
        madd.return_value = True
        math.return_value = True
        parameters = {"token":"tokennnnnn",
                      "image_id": 'containerrrrr',
                      "script": "scriptttt"}
        body = make_body(parameters)
        result = webob.Request.blank("/run",
                                     content_type="application/json",
                                     body=body,
                                     method="GET").get_response(self.app)
        self.assertEqual(405, result.status_code)

    @mock.patch.object(docker_helper.DockerController, "run_container")
    def test_run_401(self, m):
        parameters = {"token":"tokennnnnn",
                      "image_id": 'containerrrrr',
                      "script": "scriptttt"}
        body = make_body(parameters)
        result = webob.Request.blank("/run",
                                     content_type="application/json",
                                     body=body,
                                     method="PUT").get_response(self.app)
        self.assertEqual(401, result.status_code)

    @mock.patch.object(docker_helper.DockerController, "run_container")
    @mock.patch.object(credentials.UserController,
                   "authorize_image")
    @mock.patch.object(credentials.UserController,
                       "add_container")
    @mock.patch.object(docker_helper.DockerController,
                       "start_container")
    @mock.patch.object(docker_helper.DockerController,
                       "logs_container")
    def test_run_400(self, m_log, m_start, madd, math, md):
        madd.return_value = True
        math.return_value = True
        parameters = {"token":"tokennnnnn",
                      "script": "scriptttt"}
        body = make_body(parameters)
        result = webob.Request.blank("/run",
                                     content_type="application/json",
                                     body=body,
                                     method="PUT").get_response(self.app)
        self.assertEqual(400, result.status_code)

    @mock.patch.object(docker_helper.DockerController, "accounting_container")
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

    @mock.patch.object(docker_helper.DockerController, "accounting_container")
    def test_acc_401(self, m):
        parameters = {"token":"tokennnnnn",
                      "container_id": 'containerrrrr'}
        query = get_query_string(parameters)
        result = webob.Request.blank("/accounting?%s" % query,
                                     method="GET").get_response(self.app)
        self.assertEqual(401, result.status_code)

    @mock.patch.object(docker_helper.DockerController, "accounting_container")
    def test_acc_401(self, m):
        parameters = {"token":"tokennnnnn",
                      "container_id": 'containerrrrr'}
        query = get_query_string(parameters)
        result = webob.Request.blank("/accounting?%s" % query,
                                     method="GET").get_response(self.app)
        self.assertEqual(401, result.status_code)

    @mock.patch.object(docker_helper.DockerController, "accounting_container")
    def test_acc_405(self, m):
        parameters = {"token":"tokennnnnn",
                      "container_id": 'containerrrrr'}
        query = get_query_string(parameters)
        result = webob.Request.blank("/accounting?%s" % query,
                                     method="POST").get_response(self.app)
        self.assertEqual(405, result.status_code)

    @mock.patch.object(docker_helper.DockerController, "output_task")
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


    @mock.patch.object(docker_helper.DockerController, "output_task")
    def test_output_405(self, m):
        parameters = {"token":"tokennnnnn",
                      "container_id": 'containerrrrr'}
        query = get_query_string(parameters)
        result = webob.Request.blank("/output?%s" % query,
                                     method="POST").get_response(self.app)
        self.assertEqual(405, result.status_code)

    @mock.patch.object(docker_helper.DockerController, "output_task")
    def test_output_401(self, m):
        parameters = {"token":"tokennnnnn",
                      "container_id": 'containerrrrr'}
        query = get_query_string(parameters)
        result = webob.Request.blank("/output?%s" % query,
                                     method="GET").get_response(self.app)
        self.assertEqual(401, result.status_code)


    # TODO(jorgesece): test for
    # inspect and clean
    # batch configure
    # batch clean
