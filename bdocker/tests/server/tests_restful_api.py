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
import uuid
import webob

import mock

from bdocker.common import exceptions
from bdocker.server import controller
from bdocker.tests import server


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


    @mock.patch("bdocker.common.utils.load_configuration_from_file")
    @mock.patch.object(controller.ServerController, "__init__")
    def setUp(self, m_conf, m_load):
        super(TestREST, self).setUp()
        m_conf.return_value = None
        from bdocker.server import restful_api
        self.app = restful_api.app

    @mock.patch.object(controller.ServerController, "configuration")
    def test_configuration(self, m):
        m.return_value = 'tokenresult'
        parameters = {"admin_token": "tokennnnnn",
                      "user_credentials":
                          {'uid': 'uuuuuuuuuuiiiidddddd',
                           'gid': 'gggggggggguuuiiidd',
                           'job': {'id':'gggggggggguuuiiidd',
                                   'spool':'/faa'}
                           }
                      }
        body = make_body(parameters)
        result = webob.Request.blank("/configuration",
                                     method="POST",
                                     content_type="application/json",
                                     body=body).get_response(self.app)
        self.assertEqual(201, result.status_code)

    @mock.patch.object(controller.ServerController, "configuration")
    def test_configuration(self, m):
        m.side_effect = exceptions.UserCredentialsException("")
        parameters = {"admin_token": "tokennnnnn",
                      "user_credentials":
                          {'uid': 'uuuuuuuuuuiiiidddddd',
                           'gid': 'gggggggggguuuiiidd',
                           'job': {'id':'gggggggggguuuiiidd',
                                   'spool':'/faa'}
                           }
                      }
        body = make_body(parameters)
        result = webob.Request.blank("/configuration",
                                     method="POST",
                                     content_type="application/json",
                                     body=body).get_response(self.app)
        self.assertEqual(401, result.status_code)

    @mock.patch.object(controller.ServerController, "clean")
    def test_clean(self, m):
        token_admin = uuid.uuid4().hex
        token = uuid.uuid4().hex
        m.return_value = token
        parameters = {"admin_token": token_admin, "token": token}
        query = get_query_string(parameters)
        result = webob.Request.blank("/clean?%s" % query,
                                     method="DELETE",
                                     content_type="application/json"
                                     ).get_response(self.app)
        self.assertEqual(204, result.status_code)

    @mock.patch.object(controller.ServerController, "clean")
    def test_clean_401(self, m):
        token_admin = uuid.uuid4().hex
        token = uuid.uuid4().hex
        m.side_effect = exceptions.UserCredentialsException("")
        parameters = {"admin_token": token_admin, "token": token}
        query = get_query_string(parameters)
        result = webob.Request.blank("/clean?%s" % query,
                                     method="DELETE",
                                     content_type="application/json"
                                     ).get_response(self.app)
        self.assertEqual(401, result.status_code)


    @mock.patch.object(controller.ServerController, "credentials")
    def test_credentials(self, m):
        m.return_value = 'tokenresult'
        parameters = {"admin_token": "tokennnnnn",
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


    @mock.patch.object(controller.ServerController, "pull")
    def test_pull(self, md):
        im_id = 'X'
        md.return_value = {'image_id': im_id, 'status':'OK'}
        parameters = {"token":"tokennnnnn",
                      "source": 'repoooo'}
        body = make_body(parameters)
        result = webob.Request.blank("/pull",
                                     content_type="application/json",
                                     body=body,
                                     method="POST").get_response(self.app)
        self.assertEqual(201, result.status_code)

    @mock.patch.object(controller.ServerController, "pull")
    def test_pull_405(self, m):
        parameters = {"token":"tokennnnnn",
                      "source": 'repoooo'}
        body = make_body(parameters)
        result = webob.Request.blank("/pull",
                                     content_type="application/json",
                                     body=body,
                                     method="PUT").get_response(self.app)
        self.assertEqual(405, result.status_code)

    @mock.patch.object(controller.ServerController, "pull")
    def test_pull_400(self, m):
        parameters = {"token":"tokennnnnn"}
        body = make_body(parameters)
        m.side_effect = exceptions.ParseException("")
        result = webob.Request.blank("/pull",
                                     content_type="application/json",
                                     body=body,
                                     method="POST").get_response(self.app)
        self.assertEqual(400, result.status_code)

    @mock.patch.object(controller.ServerController, "delete_container")
    def test_delete(self, md):
        parameters = {"token":"tokennnnnn",
                      "container_id": 'repoooo'}
        body = make_body(parameters)
        result = webob.Request.blank("/rm",
                                     content_type="application/json",
                                     body=body,
                                     method="PUT").get_response(self.app)
        self.assertEqual(200, result.status_code)

    @mock.patch.object(controller.ServerController, "delete_container")
    def test_delete_several(self, md):
        c1 = uuid.uuid4().hex
        c2 = uuid.uuid4().hex
        md.return_value = [c1, c2]
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

    @mock.patch.object(controller.ServerController, "delete_container")
    def test_delete_405(self, m):
        parameters = {"token":"tokennnnnn",
                      "container_id": 'repoooo'}
        query = get_query_string(parameters)
        result = webob.Request.blank("/rm?%s" % query,
                                     method="GET").get_response(self.app)
        self.assertEqual(405, result.status_code)

    @mock.patch.object(controller.ServerController, "delete_container")
    def test_delete_401(self, mu):
        c1 = uuid.uuid4().hex
        c2 = uuid.uuid4().hex
        mu.side_effect = exceptions.UserCredentialsException("")
        parameters = {"token":"tokennnnnn",
                      "container_id": [c1, c2]}
        body = make_body(parameters)
        result = webob.Request.blank("/rm",
                                     content_type="application/json",
                                     body=body,
                                     method="PUT").get_response(self.app)
        self.assertEqual(401, result.status_code)

    @mock.patch.object(controller.ServerController, "list_containers")
    def test_ps(self, ml):
        token = "3333"
        all = True
        result = webob.Request.blank("/ps?token=%s&%s" % (token ,all),
                                     method="GET").get_response(self.app)
        self.assertEqual(200, result.status_code)

    @mock.patch.object(controller.ServerController, "list_containers")
    def test_ps_401(self, m):
        m.side_effect = exceptions.UserCredentialsException("")
        result = webob.Request.blank("/ps?token=333333",
                                     method="GET").get_response(self.app)
        self.assertEqual(401, result.status_code)

    @mock.patch.object(controller.ServerController, "list_containers")
    def test_ps_405(self, m):
        result = webob.Request.blank("/ps?token=333333",
                                     method="PUT").get_response(self.app)
        self.assertEqual(405, result.status_code)

    @mock.patch.object(controller.ServerController, "show")
    def test_show(self, md):
        parameters = {"token":"tokennnnnn"}
        query = get_query_string(parameters)
        result = webob.Request.blank("/inspect?%s" % query,
                                     method="GET").get_response(self.app)
        self.assertEqual(200, result.status_code)

    @mock.patch.object(controller.ServerController, "show")
    def test_show_401(self, md):
        md.side_effect = exceptions.UserCredentialsException("")
        parameters = {"token":"tokennnnnn"}
        query = get_query_string(parameters)
        result = webob.Request.blank("/inspect?%s" % query,
                                     method="GET").get_response(self.app)
        self.assertEqual(401, result.status_code)

    @mock.patch.object(controller.ServerController, "logs")
    def test_logs(self, md):
        parameters = {"token":"tokennnnnn",
                      "container_id": 'containerrrrr'}
        query = get_query_string(parameters)
        result = webob.Request.blank("/logs?%s" % query,
                                     method="GET").get_response(self.app)
        self.assertEqual(200, result.status_code)

    @mock.patch.object(controller.ServerController, "logs")
    def test_logs_401(self, m):
        m.side_effect = exceptions.UserCredentialsException("")
        parameters = {"token":"tokennnnnn",
                      "container_id": 'containerrrrr'}
        query = get_query_string(parameters)
        result = webob.Request.blank("/logs?%s" % query,
                                     method="GET").get_response(self.app)
        self.assertEqual(401, result.status_code)

    @mock.patch.object(controller.ServerController, "logs")
    def test_logs_405(self, m):
        parameters = {"token":"tokennnnnn",
                      "container_id": 'containerrrrr'}
        query = get_query_string(parameters)
        result = webob.Request.blank("/logs?%s" % query,
                                     method="POST").get_response(self.app)
        self.assertEqual(405, result.status_code)

    @mock.patch.object(controller.ServerController, "stop_container")
    def test_stop(self, md):
        parameters = {"token":"tokennnnnn",
                      "container_id": 'containerrrrr'}
        body = make_body(parameters)
        result = webob.Request.blank("/stop",
                                     content_type="application/json",
                                     body=body,
                                     method="POST").get_response(self.app)
        self.assertEqual(200, result.status_code)

    @mock.patch.object(controller.ServerController, "stop_container")
    def test_stop_405(self, m):
        parameters = {"token":"tokennnnnn",
                      "container_id": 'containerrrrr'}
        body = make_body(parameters)
        result = webob.Request.blank("/stop",
                                     content_type="application/json",
                                     body=body,
                                     method="GET").get_response(self.app)
        self.assertEqual(405, result.status_code)

    @mock.patch.object(controller.ServerController, "stop_container")
    def test_stop_401(self, m):
        m.side_effect = exceptions.UserCredentialsException("")
        parameters = {"token":"tokennnnnn",
                      "container_id": 'containerrrrr'}
        body = make_body(parameters)
        result = webob.Request.blank("/stop",
                                     content_type="application/json",
                                     body=body,
                                     method="POST").get_response(self.app)
        self.assertEqual(401, result.status_code)

    @mock.patch.object(controller.ServerController, "run")
    def test_run(self, md):
        token = uuid.uuid4().hex
        image_id = uuid.uuid4().hex
        container_id = uuid.uuid4().hex
        script = 'ls'
        detach = False
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

    @mock.patch.object(controller.ServerController, "run")
    def test_run_405(self, md):
        parameters = {"token":"tokennnnnn",
                      "image_id": 'containerrrrr',
                      "script": "scriptttt"}
        body = make_body(parameters)
        result = webob.Request.blank("/run",
                                     content_type="application/json",
                                     body=body,
                                     method="GET").get_response(self.app)
        self.assertEqual(405, result.status_code)

    @mock.patch.object(controller.ServerController, "run")
    def test_run_401(self, m):
        m.side_effect = exceptions.UserCredentialsException("")
        parameters = {"token":"tokennnnnn",
                      "image_id": 'containerrrrr',
                      "script": "scriptttt"}
        body = make_body(parameters)
        result = webob.Request.blank("/run",
                                     content_type="application/json",
                                     body=body,
                                     method="PUT").get_response(self.app)
        self.assertEqual(401, result.status_code)

    @mock.patch.object(controller.ServerController, "run")
    def test_run_400(self, md):
        parameters = {"token":"tokennnnnn",
                      "script": "scriptttt"}
        body = make_body(parameters)
        md.side_effect = exceptions.ParseException("")
        result = webob.Request.blank("/run",
                                     content_type="application/json",
                                     body=body,
                                     method="PUT").get_response(self.app)
        self.assertEqual(400, result.status_code)

    @mock.patch.object(controller.ServerController, "accounting")
    def test_acc(self, md):
        parameters = {"token":"tokennnnnn",
                      "container_id": 'containerrrrr'}
        query = get_query_string(parameters)
        result = webob.Request.blank("/accounting?%s" % query,
                                     method="GET").get_response(self.app)
        self.assertEqual(200, result.status_code)

    @mock.patch.object(controller.ServerController, "accounting")
    def test_acc_401(self, m):
        m.side_effect = exceptions.UserCredentialsException("")
        parameters = {"token":"tokennnnnn",
                      "container_id": 'containerrrrr'}
        query = get_query_string(parameters)
        result = webob.Request.blank("/accounting?%s" % query,
                                     method="GET").get_response(self.app)
        self.assertEqual(401, result.status_code)

    @mock.patch.object(controller.ServerController, "accounting")
    def test_acc_405(self, m):
        parameters = {"token":"tokennnnnn",
                      "container_id": 'containerrrrr'}
        query = get_query_string(parameters)
        result = webob.Request.blank("/accounting?%s" % query,
                                     method="POST").get_response(self.app)
        self.assertEqual(405, result.status_code)

    @mock.patch.object(controller.ServerController, "output")
    def test_output(self, md):
        parameters = {"token":"tokennnnnn",
                      "container_id": 'containerrrrr'}
        query = get_query_string(parameters)
        result = webob.Request.blank("/output?%s" % query,
                                     method="GET").get_response(self.app)
        self.assertEqual(200, result.status_code)

    @mock.patch.object(controller.ServerController, "output")
    def test_output_405(self, m):
        parameters = {"token":"tokennnnnn",
                      "container_id": 'containerrrrr'}
        query = get_query_string(parameters)
        result = webob.Request.blank("/output?%s" % query,
                                     method="POST").get_response(self.app)
        self.assertEqual(405, result.status_code)

    @mock.patch.object(controller.ServerController, "output")
    def test_output_401(self, m):
        m.side_effect = exceptions.UserCredentialsException("")
        parameters = {"token":"tokennnnnn",
                      "container_id": 'containerrrrr'}
        query = get_query_string(parameters)
        result = webob.Request.blank("/output?%s" % query,
                                     method="GET").get_response(self.app)
        self.assertEqual(401, result.status_code)



    # TODO(jorgesece): delete deprectated
    # credentials
    # batch config