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

import flask_testing as flask_tests
import mock

from bdocker.api import accounting
from bdocker.api import controller
from bdocker.api import working_node
from bdocker import exceptions
from bdocker.modules import request


class TestConfiguration(object):
    TESTING = True
    WTF_CSRF_ENABLED = False
    HASH_ROUNDS = 1


class TestAccRESTAPI(flask_tests.TestCase):
    """Test REST request mapping."""

    def create_app(self):
        accounting.app.config.from_object(TestConfiguration)
        return accounting.app

    def setUp(self):
        with mock.patch.object(controller.AccountingServerController,
                               "__init__",
                               return_value=None):
            with mock.patch("bdocker.utils.load_configuration_from_file"):
                self.app_context = self.app.app_context()
                with self.app_context:
                    accounting.load_configuration()
                    accounting.init_server()

    @mock.patch.object(controller.AccountingServerController,
                       "set_job_accounting")
    def test_set_job(self, m):
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
        with self.app_context:
            result = self.client.put("/set_accounting",
                                     method="PUT",
                                     content_type="application/json",
                                     data=body)
        self.assertEqual(201, result.status_code)


class TestWorkingNodeRESTAPI(flask_tests.TestCase):
    """Test REST request mapping."""

    def create_app(self):
        working_node.app.config.from_object(TestConfiguration)
        return working_node.app

    def setUp(self):
        with mock.patch.object(controller.ServerController,
                               "__init__",
                               return_value=None):
            with mock.patch("bdocker.utils.load_configuration_from_file"):
                self.app_context = self.app.app_context()
                with self.app_context:
                    working_node.load_configuration()
                    working_node.init_server()

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
        with self.app_context:
            result = self.client.post("/configuration",
                                      content_type="application/json",
                                  data=body)
        self.assertEqual(201, result.status_code)

    @mock.patch.object(controller.ServerController, "configuration")
    def test_configuration_401(self, m):
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
        with self.app_context:
            result = self.client.post("/configuration",
                                  content_type="application/json",
                                  data=body)
        self.assertEqual(401, result.status_code)

    @mock.patch.object(controller.ServerController, "clean")
    def test_clean(self, m):
        token_admin = uuid.uuid4().hex
        token = uuid.uuid4().hex
        m.return_value = token
        parameters = {"admin_token": token_admin, "token": token}
        query = request.get_query_string(parameters)
        with self.app_context:
            result = self.client.delete("/clean?%s" % query)
        self.assertEqual(204, result.status_code)

    @mock.patch.object(controller.ServerController, "clean")
    def test_clean_401(self, m):
        token_admin = uuid.uuid4().hex
        token = uuid.uuid4().hex
        m.side_effect = exceptions.UserCredentialsException("")
        parameters = {"admin_token": token_admin, "token": token}
        query = request.get_query_string(parameters)
        with self.app_context:
                    result = self.client.delete("/clean?%s" % query)
        self.assertEqual(401, result.status_code)

    @mock.patch.object(controller.ServerController, "pull")
    def test_pull(self, md):
        im_id = 'X'
        md.return_value = {'image_id': im_id, 'status': 'OK'}
        parameters = {"token": "tokennnnnn",
                      "source": 'repoooo'}
        body = request.make_body(parameters)
        with self.app_context:
            result = self.client.post("/pull",
                                     content_type="application/json",
                                     data=body)
        self.assertEqual(201, result.status_code)

    @mock.patch.object(controller.ServerController, "pull")
    def test_pull_405(self, m):
        parameters = {"token": "tokennnnnn",
                      "source": 'repoooo'}
        body = request.make_body(parameters)
        with self.app_context:
            result = self.client.put("/pull",
                                     content_type="application/json",
                                     data=body)
        self.assertEqual(405, result.status_code)

    @mock.patch.object(controller.ServerController, "pull")
    def test_pull_400(self, m):
        parameters = {"token": "tokennnnnn"}
        body = request.make_body(parameters)
        m.side_effect = exceptions.ParseException("")
        with self.app_context:
            result = self.client.post("/pull",
                                     content_type="application/json",
                                     data=body
                                     )
        self.assertEqual(400, result.status_code)

    @mock.patch.object(controller.ServerController,
                       "delete_container")
    def test_delete(self, md):
        parameters = {"token": "tokennnnnn",
                      "container_id": 'repoooo'}
        body = request.make_body(parameters)
        with self.app_context:
            result = self.client.put("/rm",
                                     content_type="application/json",
                                     data=body
                                     )
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
        with self.app_context:
            result = self.client.put("/rm",
                                     content_type="application/json",
                                     data=body
                                     )
        self.assertEqual(200, result.status_code)
        self.assertEqual(c1, result.json["results"][0])
        self.assertEqual(c2, result.json["results"][1])
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
        with self.app_context:
            result = self.client.put("/rm",
                                     content_type="application/json",
                                     data=body
                                     )
        self.assertEqual(200, result.status_code)
        self.assertEqual(force, md.call_args_list[0][0][0]["force"])

    @mock.patch.object(controller.ServerController, "delete_container")
    def test_delete_405(self, m):
        parameters = {"token": "tokennnnnn",
                      "container_id": 'repoooo'}
        query = request.get_query_string(parameters)
        with self.app_context:
            result = self.client.get("/rm?%s" % query,
                                     )
        self.assertEqual(405, result.status_code)

    @mock.patch.object(controller.ServerController, "delete_container")
    def test_delete_401(self, mu):
        c1 = uuid.uuid4().hex
        c2 = uuid.uuid4().hex
        mu.side_effect = exceptions.UserCredentialsException("")
        parameters = {"token": "tokennnnnn",
                      "container_id": [c1, c2]}
        body = request.make_body(parameters)
        with self.app_context:
            result = self.client.put("/rm",
                                     content_type="application/json",
                                     data=body
                                     )
        self.assertEqual(401, result.status_code)

    @mock.patch.object(controller.ServerController, "list_containers")
    def test_ps(self, ml):
        token = "3333"
        all_containers = True
        with self.app_context:
            result = self.client.get(
            "/ps?token=%s&all=%s" % (token, all_containers),
            )
        self.assertEqual(200, result.status_code)
        self.assertEqual(token, ml.call_args_list[0][0][0]["token"])
        self.assertEqual(str(all_containers),
                         ml.call_args_list[0][0][0]["all"])

    @mock.patch.object(controller.ServerController,
                       "list_containers")
    def test_ps_401(self, m):
        m.side_effect = exceptions.UserCredentialsException("")
        with self.app_context:
            result = self.client.get("/ps?token=333333",
                                     )
        self.assertEqual(401, result.status_code)

    @mock.patch.object(controller.ServerController, "list_containers")
    def test_ps_405(self, m):
        with self.app_context:
            result = self.client.put("/ps?token=333333",
                                     )
        self.assertEqual(405, result.status_code)

    @mock.patch.object(controller.ServerController, "show")
    def test_show(self, md):
        parameters = {"token": "tokennnnnn"}
        query = request.get_query_string(parameters)
        with self.app_context:
            result = self.client.get("/inspect?%s" % query,
                                     )
        self.assertEqual(200, result.status_code)

    @mock.patch.object(controller.ServerController, "show")
    def test_show_401(self, md):
        md.side_effect = exceptions.UserCredentialsException("")
        parameters = {"token": "tokennnnnn"}
        query = request.get_query_string(parameters)
        with self.app_context:
            result = self.client.get("/inspect?%s" % query,
                                     )
        self.assertEqual(401, result.status_code)

    @mock.patch.object(controller.ServerController, "logs")
    def test_logs(self, md):
        parameters = {"token": "tokennnnnn",
                      "container_id": 'containerrrrr'}
        query = request.get_query_string(parameters)
        with self.app_context:
            result = self.client.get("/logs?%s" % query,
                                     )
        self.assertEqual(200, result.status_code)

    @mock.patch.object(controller.ServerController, "logs")
    def test_logs_401(self, m):
        m.side_effect = exceptions.UserCredentialsException("")
        parameters = {"token": "tokennnnnn",
                      "container_id": 'containerrrrr'}
        query = request.get_query_string(parameters)
        with self.app_context:
            result = self.client.get("/logs?%s" % query,
                                     )
        self.assertEqual(401, result.status_code)

    @mock.patch.object(controller.ServerController, "logs")
    def test_logs_405(self, m):
        parameters = {"token": "tokennnnnn",
                      "container_id": 'containerrrrr'}
        query = request.get_query_string(parameters)
        with self.app_context:
            result = self.client.put("/logs?%s" % query,
                                     )
        self.assertEqual(405, result.status_code)

    @mock.patch.object(controller.ServerController, "stop_container")
    def test_stop(self, md):
        parameters = {"token": "tokennnnnn",
                      "container_id": 'containerrrrr'}
        body = request.make_body(parameters)
        with self.app_context:
            result = self.client.put("/stop",
                                     content_type="application/json",
                                     data=body
                                     )
        self.assertEqual(200, result.status_code)

    @mock.patch.object(controller.ServerController, "stop_container")
    def test_stop_405(self, m):
        parameters = {"token": "tokennnnnn",
                      "container_id": 'containerrrrr'}
        body = request.make_body(parameters)
        with self.app_context:
            result = self.client.post("/stop",
                                     content_type="application/json",
                                     data=body
                                     )
        self.assertEqual(405, result.status_code)

    @mock.patch.object(controller.ServerController, "stop_container")
    def test_stop_401(self, m):
        m.side_effect = exceptions.UserCredentialsException("")
        parameters = {"token": "tokennnnnn",
                      "container_id": 'containerrrrr'}
        body = request.make_body(parameters)
        with self.app_context:
            result = self.client.put("/stop",
                                     content_type="application/json",
                                     data=body
                                     )
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
        with self.app_context:
            result = self.client.put("/run",
                                     content_type="application/json",
                                     data=body
                                     )
        self.assertEqual(201, result.status_code)
        self.assertEqual(container_id, result.json["results"]["Id"])

    @mock.patch.object(controller.ServerController, "run")
    def test_run_405(self, md):
        parameters = {"token": "tokennnnnn",
                      "image_id": 'containerrrrr',
                      "script": "scriptttt"}
        body = request.make_body(parameters)
        with self.app_context:
            result = self.client.post("/run",
                                     content_type="application/json",
                                     data=body
                                     )
        self.assertEqual(405, result.status_code)

    @mock.patch.object(controller.ServerController, "run")
    def test_run_401(self, m):
        m.side_effect = exceptions.UserCredentialsException("")
        parameters = {"token": "tokennnnnn",
                      "image_id": 'containerrrrr',
                      "script": "scriptttt"}
        body = request.make_body(parameters)
        with self.app_context:
            result = self.client.put("/run",
                                     content_type="application/json",
                                     data=body
                                     )
        self.assertEqual(401, result.status_code)

    @mock.patch.object(controller.ServerController, "run")
    def test_run_400(self, md):
        parameters = {"token": "tokennnnnn",
                      "script": "scriptttt"}
        body = request.make_body(parameters)
        md.side_effect = exceptions.ParseException("")
        with self.app_context:
            result = self.client.put("/run",
                                     content_type="application/json",
                                     data=body
                                     )
        self.assertEqual(400, result.status_code)

    @mock.patch.object(controller.ServerController, "notify_accounting")
    def test_notify_acc(self, md):
        parameters = {"token": uuid.uuid4().hex,
                      "admin_token": uuid.uuid4().hex}
        body = request.make_body(parameters)
        with self.app_context:
            result = self.client.put("/notify_accounting",
                                     content_type="application/json",
                                     data=body
                                     )
        self.assertEqual(201, result.status_code)

    @mock.patch.object(controller.ServerController, "notify_accounting")
    def test_notify_acc_401(self, m):
        m.side_effect = exceptions.UserCredentialsException("")
        parameters = {"token": uuid.uuid4().hex,
                      "admin_token": uuid.uuid4().hex}
        body = request.make_body(parameters)
        with self.app_context:
            result = self.client.put("/notify_accounting",
                                     content_type="application/json",
                                     data=body
                                     )
        self.assertEqual(401, result.status_code)

    @mock.patch.object(controller.ServerController, "notify_accounting")
    def test_notify_acc_405(self, m):
        parameters = {"token": uuid.uuid4().hex,
                      "admin_token": uuid.uuid4().hex}
        query = request.get_query_string(parameters)
        with self.app_context:
            result = self.client.get("/notify_accounting?%s" % query,
                                     )
        self.assertEqual(405, result.status_code)

    @mock.patch.object(controller.ServerController, "copy")
    def test_output(self, md):
        parameters = {"token": "tokennnnnn",
                      "container_id": 'containerrrrr',
                      "path": "/foo"}
        body = request.make_body(parameters)
        with self.app_context:
            result = self.client.put("/copy",
                                     content_type="application/json",
                                     data=body
                                     )
        self.assertEqual(201, result.status_code)

    @mock.patch.object(controller.ServerController, "copy")
    def test_output_405(self, m):
        parameters = {"token": "tokennnnnn",
                      "container_id": 'containerrrrr',
                      "path": "/foo"}
        query = request.get_query_string(parameters)
        with self.app_context:
            result = self.client.post("/copy?%s" % query,
                                     )
        self.assertEqual(405, result.status_code)

    @mock.patch.object(controller.ServerController, "copy")
    def test_output_401(self, m):
        m.side_effect = exceptions.UserCredentialsException("")
        parameters = {"token": "tokennnnnn",
                      "container_id": 'containerrrrr',
                      "path": "/foo"}
        body = request.make_body(parameters)
        with self.app_context:
            result = self.client.put("/copy",
                                     content_type="application/json",
                                     data=body
                                     )
        self.assertEqual(401, result.status_code)
