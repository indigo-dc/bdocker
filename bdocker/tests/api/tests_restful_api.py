# -*- coding: utf-8 -*-

# Copyright 2015 LIP - INDIGO-DataCloud
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

import uuid

import mock
import testtools
import webob

from bdocker import exceptions
from bdocker.modules import request
from bdocker.api import controller


class TestAccRESTAPI(testtools.TestCase):
    """Test REST request mapping."""

    def setUp(self):
        super(TestAccRESTAPI, self).setUp()
        with mock.patch.object(controller.AccountingServerController,
                               "__init__",
                               return_value=None):
            with mock.patch("bdocker.utils.load_configuration_from_file"):
                from bdocker.api import accounting
                self.app = accounting.app

    @mock.patch.object(controller.AccountingServerController, "set_job_accounting")
    def test_set_job(self, m):
        pass
        m.return_value = 'tokenresult'
        parameters = {"admin_token": "tokennnnnn",
                      "user_credentials":
                          {'uid': 'uuuuuuuuuuiiiidddddd',
                           'gid': 'gggggggggguuuiiidd',
                           'job': {'id': 'gggggggggguuuiiidd',
                                   'spool': '/faa'}
                           }
                      }
        body = request.make_body(parameters)
        result = webob.Request.blank("/set_accounting",
                                     method="PUT",
                                     content_type="application/json",
                                     body=body).get_response(self.app)
        self.assertEqual(201, result.status_code)


class TestWorkingNodeRESTAPI(testtools.TestCase):
    """Test REST request mapping."""

    def setUp(self):
        super(TestWorkingNodeRESTAPI, self).setUp()
        with mock.patch.object(controller.ServerController,
                               "__init__",
                               return_value=None):
            with mock.patch("bdocker.utils.load_configuration_from_file"):
                from bdocker.api import working_node
                self.app = working_node.app

    @mock.patch.object(controller.ServerController, "configuration")
    def test_configuration(self, m):
        m.return_value = 'tokenresult'
        parameters = {"admin_token": "tokennnnnn",
                      "user_credentials":
                          {'uid': 'uuuuuuuuuuiiiidddddd',
                           'gid': 'gggggggggguuuiiidd',
                           'job': {'id': 'gggggggggguuuiiidd',
                                   'spool': '/faa'}
                           }
                      }
        body = request.make_body(parameters)
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
                           'job': {'id': 'gggggggggguuuiiidd',
                                   'spool': '/faa'}
                           }
                      }
        body = request.make_body(parameters)
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
        query = request.get_query_string(parameters)
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
        query = request.get_query_string(parameters)
        result = webob.Request.blank("/clean?%s" % query,
                                     method="DELETE",
                                     content_type="application/json"
                                     ).get_response(self.app)
        self.assertEqual(401, result.status_code)

    @mock.patch.object(controller.ServerController, "pull")
    def test_pull(self, md):
        im_id = 'X'
        md.return_value = {'image_id': im_id, 'status': 'OK'}
        parameters = {"token": "tokennnnnn",
                      "source": 'repoooo'}
        body = request.make_body(parameters)
        result = webob.Request.blank("/pull",
                                     content_type="application/json",
                                     body=body,
                                     method="POST").get_response(self.app)
        self.assertEqual(201, result.status_code)

    @mock.patch.object(controller.ServerController, "pull")
    def test_pull_405(self, m):
        parameters = {"token": "tokennnnnn",
                      "source": 'repoooo'}
        body = request.make_body(parameters)
        result = webob.Request.blank("/pull",
                                     content_type="application/json",
                                     body=body,
                                     method="PUT").get_response(self.app)
        self.assertEqual(405, result.status_code)

    @mock.patch.object(controller.ServerController, "pull")
    def test_pull_400(self, m):
        parameters = {"token": "tokennnnnn"}
        body = request.make_body(parameters)
        m.side_effect = exceptions.ParseException("")
        result = webob.Request.blank("/pull",
                                     content_type="application/json",
                                     body=body,
                                     method="POST").get_response(self.app)
        self.assertEqual(400, result.status_code)

    @mock.patch.object(controller.ServerController,
                       "delete_container")
    def test_delete(self, md):
        parameters = {"token": "tokennnnnn",
                      "container_id": 'repoooo'}
        body = request.make_body(parameters)
        result = webob.Request.blank("/rm",
                                     content_type="application/json",
                                     body=body,
                                     method="PUT").get_response(self.app)
        self.assertEqual(200, result.status_code)

    @mock.patch.object(controller.ServerController,
                       "delete_container")
    def test_delete_several(self, md):
        c1 = uuid.uuid4().hex
        c2 = uuid.uuid4().hex
        token = uuid.uuid4().hex
        force = False
        md.return_value = [c1, c2]
        parameters = {"token": token,
                      "container_id": [c1, c2],
                      "force": force}
        body = request.make_body(parameters)
        result = webob.Request.blank("/rm",
                                     content_type="application/json",
                                     body=body,
                                     method="PUT").get_response(self.app)
        self.assertEqual(200, result.status_code)
        self.assertEqual(c1, result.json_body["results"][0])
        self.assertEqual(c2, result.json_body["results"][1])
        self.assertEqual(token, md.call_args_list[0][0][0]["token"])
        self.assertEqual(force, md.call_args_list[0][0][0]["force"])

    @mock.patch.object(controller.ServerController, "delete_container")
    def test_delete_force(self, md):
        c1 = uuid.uuid4().hex
        c2 = uuid.uuid4().hex
        token = uuid.uuid4().hex
        force = True
        md.return_value = [c1, c2]
        parameters = {"token": token,
                      "container_id": [c1],
                      "force": force}
        body = request.make_body(parameters)
        result = webob.Request.blank("/rm",
                                     content_type="application/json",
                                     body=body,
                                     method="PUT").get_response(self.app)
        self.assertEqual(200, result.status_code)
        self.assertEqual(force, md.call_args_list[0][0][0]["force"])

    @mock.patch.object(controller.ServerController, "delete_container")
    def test_delete_405(self, m):
        parameters = {"token": "tokennnnnn",
                      "container_id": 'repoooo'}
        query = request.get_query_string(parameters)
        result = webob.Request.blank("/rm?%s" % query,
                                     method="GET").get_response(self.app)
        self.assertEqual(405, result.status_code)

    @mock.patch.object(controller.ServerController, "delete_container")
    def test_delete_401(self, mu):
        c1 = uuid.uuid4().hex
        c2 = uuid.uuid4().hex
        mu.side_effect = exceptions.UserCredentialsException("")
        parameters = {"token": "tokennnnnn",
                      "container_id": [c1, c2]}
        body = request.make_body(parameters)
        result = webob.Request.blank("/rm",
                                     content_type="application/json",
                                     body=body,
                                     method="PUT").get_response(self.app)
        self.assertEqual(401, result.status_code)

    @mock.patch.object(controller.ServerController, "list_containers")
    def test_ps(self, ml):
        token = "3333"
        all_containers = True
        result = webob.Request.blank(
            "/ps?token=%s&all=%s" % (token, all_containers),
            method="GET").get_response(self.app)
        self.assertEqual(200, result.status_code)
        self.assertEqual(token, ml.call_args_list[0][0][0]["token"])
        self.assertEqual(str(all_containers), ml.call_args_list[0][0][0]["all"])

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
        parameters = {"token": "tokennnnnn"}
        query = request.get_query_string(parameters)
        result = webob.Request.blank("/inspect?%s" % query,
                                     method="GET").get_response(self.app)
        self.assertEqual(200, result.status_code)

    @mock.patch.object(controller.ServerController, "show")
    def test_show_401(self, md):
        md.side_effect = exceptions.UserCredentialsException("")
        parameters = {"token": "tokennnnnn"}
        query = request.get_query_string(parameters)
        result = webob.Request.blank("/inspect?%s" % query,
                                     method="GET").get_response(self.app)
        self.assertEqual(401, result.status_code)

    @mock.patch.object(controller.ServerController, "logs")
    def test_logs(self, md):
        parameters = {"token": "tokennnnnn",
                      "container_id": 'containerrrrr'}
        query = request.get_query_string(parameters)
        result = webob.Request.blank("/logs?%s" % query,
                                     method="GET").get_response(self.app)
        self.assertEqual(200, result.status_code)

    @mock.patch.object(controller.ServerController, "logs")
    def test_logs_401(self, m):
        m.side_effect = exceptions.UserCredentialsException("")
        parameters = {"token": "tokennnnnn",
                      "container_id": 'containerrrrr'}
        query = request.get_query_string(parameters)
        result = webob.Request.blank("/logs?%s" % query,
                                     method="GET").get_response(self.app)
        self.assertEqual(401, result.status_code)

    @mock.patch.object(controller.ServerController, "logs")
    def test_logs_405(self, m):
        parameters = {"token": "tokennnnnn",
                      "container_id": 'containerrrrr'}
        query = request.get_query_string(parameters)
        result = webob.Request.blank("/logs?%s" % query,
                                     method="POST").get_response(self.app)
        self.assertEqual(405, result.status_code)

    @mock.patch.object(controller.ServerController, "stop_container")
    def test_stop(self, md):
        parameters = {"token": "tokennnnnn",
                      "container_id": 'containerrrrr'}
        body = request.make_body(parameters)
        result = webob.Request.blank("/stop",
                                     content_type="application/json",
                                     body=body,
                                     method="POST").get_response(self.app)
        self.assertEqual(200, result.status_code)

    @mock.patch.object(controller.ServerController, "stop_container")
    def test_stop_405(self, m):
        parameters = {"token": "tokennnnnn",
                      "container_id": 'containerrrrr'}
        body = request.make_body(parameters)
        result = webob.Request.blank("/stop",
                                     content_type="application/json",
                                     body=body,
                                     method="GET").get_response(self.app)
        self.assertEqual(405, result.status_code)

    @mock.patch.object(controller.ServerController, "stop_container")
    def test_stop_401(self, m):
        m.side_effect = exceptions.UserCredentialsException("")
        parameters = {"token": "tokennnnnn",
                      "container_id": 'containerrrrr'}
        body = request.make_body(parameters)
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
        body = request.make_body(parameters)
        result = webob.Request.blank("/run",
                                     content_type="application/json",
                                     body=body,
                                     method="PUT").get_response(self.app)
        self.assertEqual(201, result.status_code)
        # todo: parse to get id

    @mock.patch.object(controller.ServerController, "run")
    def test_run_405(self, md):
        parameters = {"token": "tokennnnnn",
                      "image_id": 'containerrrrr',
                      "script": "scriptttt"}
        body = request.make_body(parameters)
        result = webob.Request.blank("/run",
                                     content_type="application/json",
                                     body=body,
                                     method="GET").get_response(self.app)
        self.assertEqual(405, result.status_code)

    @mock.patch.object(controller.ServerController, "run")
    def test_run_401(self, m):
        m.side_effect = exceptions.UserCredentialsException("")
        parameters = {"token": "tokennnnnn",
                      "image_id": 'containerrrrr',
                      "script": "scriptttt"}
        body = request.make_body(parameters)
        result = webob.Request.blank("/run",
                                     content_type="application/json",
                                     body=body,
                                     method="PUT").get_response(self.app)
        self.assertEqual(401, result.status_code)

    @mock.patch.object(controller.ServerController, "run")
    def test_run_400(self, md):
        parameters = {"token": "tokennnnnn",
                      "script": "scriptttt"}
        body = request.make_body(parameters)
        md.side_effect = exceptions.ParseException("")
        result = webob.Request.blank("/run",
                                     content_type="application/json",
                                     body=body,
                                     method="PUT").get_response(self.app)
        self.assertEqual(400, result.status_code)

    @mock.patch.object(controller.ServerController, "notify_accounting")
    def test_notify_acc(self, md):
        parameters = {"token": uuid.uuid4().hex,
                      "admin_token": uuid.uuid4().hex}
        body = request.make_body(parameters)
        result = webob.Request.blank("/notify_accounting",
                                     content_type="application/json",
                                     body=body,
                                     method="PUT").get_response(self.app)
        self.assertEqual(201, result.status_code)

    @mock.patch.object(controller.ServerController, "notify_accounting")
    def test_notify_acc_401(self, m):
        m.side_effect = exceptions.UserCredentialsException("")
        parameters = {"token": uuid.uuid4().hex,
                      "admin_token": uuid.uuid4().hex}
        body = request.make_body(parameters)
        result = webob.Request.blank("/notify_accounting",
                                     content_type="application/json",
                                     body=body,
                                     method="PUT").get_response(self.app)
        self.assertEqual(401, result.status_code)

    @mock.patch.object(controller.ServerController, "notify_accounting")
    def test_notify_acc_405(self, m):
        parameters = {"token": uuid.uuid4().hex,
                      "admin_token": uuid.uuid4().hex}
        query = request.get_query_string(parameters)
        result = webob.Request.blank("/notify_accounting?%s" % query,
                                     method="GET").get_response(self.app)
        self.assertEqual(405, result.status_code)

    @mock.patch.object(controller.ServerController, "copy")
    def test_output(self, md):
        parameters = {"token": "tokennnnnn",
                      "container_id": 'containerrrrr',
                      "path": "/foo"}
        body = request.make_body(parameters)
        result = webob.Request.blank("/copy",
                                     content_type="application/json",
                                     body=body,
                                     method="PUT").get_response(self.app)
        self.assertEqual(201, result.status_code)

    @mock.patch.object(controller.ServerController, "copy")
    def test_output_405(self, m):
        parameters = {"token": "tokennnnnn",
                      "container_id": 'containerrrrr',
                      "path": "/foo"}
        query = request.get_query_string(parameters)
        result = webob.Request.blank("/copy?%s" % query,
                                     method="POST").get_response(self.app)
        self.assertEqual(405, result.status_code)

    @mock.patch.object(controller.ServerController, "copy")
    def test_output_401(self, m):
        m.side_effect = exceptions.UserCredentialsException("")
        parameters = {"token": "tokennnnnn",
                      "container_id": 'containerrrrr',
                      "path": "/foo"}
        body = request.make_body(parameters)
        result = webob.Request.blank("/copy",
                                     content_type="application/json",
                                     body=body,
                                     method="PUT").get_response(self.app)
        self.assertEqual(401, result.status_code)

