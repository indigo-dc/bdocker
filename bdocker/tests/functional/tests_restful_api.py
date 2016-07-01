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

import docker as docker_py
import json
import uuid

import mock
import os
import testtools
import webob
from cgroupspy import nodes

from bdocker.modules import request


def create_fake_json_resp(data, status=200):
    r = webob.Response()
    r.headers["Content-Type"] = "application/json"
    r.charset = "utf8"
    r.body = json.dumps(data).encode("utf8")
    r.status_code = status
    return r


class TestAccRESTAPI(testtools.TestCase):
    """Test REST request mapping."""
    @mock.patch("bdocker.utils.read_yaml_file")
    def setUp(self, m_file):
        super(TestAccRESTAPI, self).setUp()
        file_name = os.path.join(os.path.dirname(__file__),
                                 'sge_accounting_configure.cfg')
        self.admin_token = uuid.uuid4().hex
        self.user_token = uuid.uuid4().hex
        token_store = {
            "prolog": {"token":self.admin_token},
            self.user_token: {
                "uid": uuid.uuid4().hex,
                "gid": uuid.uuid4().hex,
                "home_dir": "/foo",
                "job": {
                    "id": uuid.uuid4().hex,
                    "spool": "/baa"}
            }}
        m_file.return_value = token_store
        os.environ['BDOCKER_CONF_FILE'] = file_name
        from bdocker.api import accounting
        self.app = accounting.app

    @mock.patch("__builtin__.open")
    def test_set_job(self, m_file):
        line = ("docker:ge-wn03.novalocal:hpc:jorgesece:bdocker_job.sh.o80:81:sge:15:1465486337:"
        "1465486332:1465486332:0:127:0:0.053201:0.100611:5632.000000:0:0:0:0:25024:0:0:0.000000:"
        "72:0:0:0:242:55:NONE:sysusers:NONE:1:0:0.000000:0.000000:0.000000:-U sysusers:0.000000:"
        "NONE:0.000000:0:0"
        )
        m_class = mock.MagicMock()
        m_class.readline.return_value = line
        m_file.return_value = m_class
        parameters = {"admin_token": self.admin_token,
                      "accounting": line
                      }
        body = request.make_body(parameters)
        result = webob.Request.blank("/set_accounting",
                                     method="PUT",
                                     content_type="application/json",
                                     body=body).get_response(self.app)
        self.assertEqual(201, result.status_code)

fake = {"admin_token": uuid.uuid4().hex,
        "user_token": uuid.uuid4().hex,
        "user_uid": uuid.uuid4().hex,
        "user_gid": uuid.uuid4().hex,
        "job_id": uuid.uuid4().hex,
        "c1": uuid.uuid4().hex,
        "c2": uuid.uuid4().hex,
        }

class TestIntegrationWN(testtools.TestCase):
    """Test REST request mapping."""

    @mock.patch("bdocker.utils.read_yaml_file")
    def setUp(self, m_file):
        super(TestIntegrationWN, self).setUp()
        file_name = os.path.join(os.path.dirname(__file__),
                                 'sge_wn_configure.cfg')
        self.admin_token = fake["admin_token"]
        self.user_token = fake["user_token"]
        self.user_uid = fake["user_uid"]
        self.user_gid = fake["user_gid"]
        self.user_home = "/foo"
        self.job_id = fake["job_id"]
        self.c1 = fake["c1"]
        self.c2 = fake["c2"]
        self.job_info =  {
                    "job_id": self.job_id,
                    "spool": "/baa",
                    "max_cpu": 0,
                    "max_memory": 0,
                    "user_name": "",
                    "queue_name": "",
                    "host_name": "",
                    "job_name": "",
                    "account_name": "",
                    "log_name": ""}
        # TODO(jorgesece): in parallel
        # it delete tokens and it giveus error
        self.token_store = {
            "prolog": {"token": self.admin_token},
            self.user_token: {
                "uid": self.user_uid,
                "gid": self.user_gid,
                "home": self.user_home,
                "job": self.job_info,
                "containers":[self.c1, self.c2]}
        }
        m_file.return_value = self.token_store
        os.environ['BDOCKER_CONF_FILE'] = file_name
        from bdocker.api import working_node
        self.app = working_node.app

    @mock.patch("pwd.getpwuid")
    @mock.patch("os.path.realpath")
    @mock.patch("bdocker.utils.write_yaml_file")
    @mock.patch("bdocker.utils.read_yaml_file")
    @mock.patch("bdocker.utils.read_file")
    @mock.patch.object(nodes.Node, "create_cgroup")
    @mock.patch.object(uuid, "uuid4")
    @mock.patch("os.fork")
    def test_configuration(self, m_fork,
                           m_uuid, m_cre, m_r, m_ry, m_w,
                           m_path, m_getpi):
        parameters = {"admin_token": self.admin_token,
                      "user_credentials":
                          {'uid': self.user_uid,
                           'gid': self.user_gid,
                           "home": self.user_home,
                           'job': {'job_id': self.job_id,
                                   'spool': '/faa',
                                   "max_cpu": 0,
                                   "max_memory": 0,
                                   "user_name": "",
                                   "queue_name": "",
                                   "host_name": "",
                                   "job_name": "",
                                   "account_name": "",
                                   "log_name": ""}
                           }
                      }
        m_ry.return_value = self.token_store
        mock_uid = mock.MagicMock()
        mock_uid.hex = self.user_token
        m_uuid.return_value = mock_uid
        m_class = mock.MagicMock()
        m_class.pw_gid = self.user_gid
        m_getpi.return_value = m_class
        m_path.return_value = self.user_home
        body = request.make_body(parameters)
        result = webob.Request.blank("/configuration",
                                     method="POST",
                                     content_type="application/json",
                                     body=body).get_response(self.app)
        self.assertEqual(201, result.status_code)
        self.assertEqual(self.user_token,
                         result.json_body["results"])

    @mock.patch.object(nodes.Node, "delete_cgroup")
    @mock.patch("bdocker.utils.read_file")
    @mock.patch("bdocker.utils.add_to_file")
    @mock.patch("bdocker.utils.delete_file")
    @mock.patch("bdocker.utils.read_yaml_file")
    @mock.patch("bdocker.utils.write_yaml_file")
    @mock.patch.object(request.RequestController, "_get_req")
    @mock.patch.object(docker_py.Client, "remove_container")
    def test_clean(self, m_dock, m_rq, m_w, m_ry, m_del, m_add, m_r, m_delgroup):
        out = create_fake_json_resp(
            {}, 204)
        m_rq.return_value.get_response.return_value = out
        m_r.return_value = "2222\n3333"
        m_ry.side_effect = [self.job_info, self.token_store]
        parameters = {"admin_token": self.admin_token,
                      "token": self.user_token,}
        query = request.get_query_string(parameters)
        result = webob.Request.blank("/clean?%s" % query,
                                     method="DELETE",
                                     content_type="application/json"
                                     ).get_response(self.app)
        self.assertEqual(204, result.status_code)

    @mock.patch.object(docker_py.Client, "pull")
    def test_pull(self, md):
        parameters = {"token": self.user_token,
                      "source": 'repoooo'}
        body = request.make_body(parameters)
        result = webob.Request.blank("/pull",
                                     content_type="application/json",
                                     body=body,
                                     method="POST").get_response(self.app)
        self.assertEqual(201, result.status_code)

    @mock.patch.object(docker_py.Client, "remove_container")
    def test_delete(self, md):
        parameters = {"token": self.user_token,
                      "container_id": 'repoooo'}
        body = request.make_body(parameters)
        result = webob.Request.blank("/rm",
                                     content_type="application/json",
                                     body=body,
                                     method="PUT").get_response(self.app)
        self.assertEqual(201, result.status_code)

    @mock.patch.object(docker_py.Client, "remove_container")
    @mock.patch("bdocker.utils.write_yaml_file")
    @mock.patch("bdocker.utils.read_yaml_file")
    def test_delete_several(self, m_r, m_w, md):
        m_r.return_value = self.token_store
        force = False
        parameters = {"token": self.user_token,
                      "container_id": [self.c1, self.c2],
                      "force": force}
        body = request.make_body(parameters)
        result = webob.Request.blank("/rm",
                                     content_type="application/json",
                                     body=body,
                                     method="PUT").get_response(self.app)
        self.assertEqual(201, result.status_code)
        self.assertEqual(self.c1, result.json_body["results"][0])
        self.assertEqual(self.c2, result.json_body["results"][1])

    @mock.patch.object(docker_py.Client, "containers")
    def test_ps(self, ml):
        ml.return_value = [
            {"Id": self.c1,
             "Created": 666.777,
             "Names": ["y"],
             "Ports":["z"],
             "Image": "image_name",
             "Command": "ls",
             "Status": "status"},
            {"Id": self.c2,
             "Created": 666.777,
             "Names": ["y"],
             "Ports":["z"],
             "Image": "image_name",
             "Command": "ls",
             "Status": "status"}]
        token = self.user_token
        all = True
        result = webob.Request.blank("/ps?token=%s&all=%s" % (token, all),
                                     method="GET").get_response(self.app)
        self.assertEqual(200, result.status_code)
        self.assertIn(result.json_body["results"][0][0], self.c1)
        self.assertIn(result.json_body["results"][1][0], self.c2)

    @mock.patch.object(docker_py.Client, "inspect_container")
    def test_show(self, md):
        md.return_value = {}
        parameters = {"token": self.user_token,
                      "container_id": self.c1}
        query = request.get_query_string(parameters)
        result = webob.Request.blank("/inspect?%s" % query,
                                     method="GET").get_response(self.app)
        self.assertEqual(200, result.status_code)

    @mock.patch.object(docker_py.Client, "logs")
    def test_logs(self, md):
        parameters = {"token": self.user_token,
                      "container_id": self.c1}
        query = request.get_query_string(parameters)
        result = webob.Request.blank("/logs?%s" % query,
                                     method="GET").get_response(self.app)
        self.assertEqual(200, result.status_code)

    @mock.patch.object(docker_py.Client, "stop")
    def test_stop(self, md):
        parameters = {"token": self.user_token,
                      "container_id": self.c1}
        body = request.make_body(parameters)
        result = webob.Request.blank("/stop",
                                     content_type="application/json",
                                     body=body,
                                     method="POST").get_response(self.app)
        self.assertEqual(200, result.status_code)

    # @mock.patch.object(docker_py.Client, "stop")
    # def test_run(self, md):
    #     token = uuid.uuid4().hex
    #     image_id = uuid.uuid4().hex
    #     container_id = uuid.uuid4().hex
    #     script = 'ls'
    #     detach = False
    #     md.return_value = {'Id': container_id}
    #     parameters = {"token": token,
    #                   "image_id": image_id,
    #                   "script": script,
    #                   "detach": detach
    #                   }
    #     body = request.make_body(parameters)
    #     result = webob.Request.blank("/run",
    #                                  content_type="application/json",
    #                                  body=body,
    #                                  method="PUT").get_response(self.app)
    #     self.assertEqual(201, result.status_code)
    #     # todo: parse to get id


    @mock.patch.object(docker_py.Client, "put_archive")
    @mock.patch("bdocker.utils.read_tar_raw_data_stream")
    def test_cp_to_container(self, m_str, _md):
        parameters = {"token": self.user_token,
                      "container_id": self.c1,
                      "container_path": "/foo",
                      "host_path": "/foo",
                      "host_to_container": True}
        body = request.make_body(parameters)
        result = webob.Request.blank("/copy",
                                     content_type="application/json",
                                     body=body,
                                     method="PUT").get_response(self.app)
        self.assertEqual(201, result.status_code)

    @mock.patch.object(docker_py.Client, "get_archive")
    @mock.patch("bdocker.utils.write_tar_raw_data_stream")
    def test_cp_from_container(self, m_str, m_g):
        out = mock.MagicMock()
        out.data = None
        stat = "OK"
        m_g.return_value = out, stat
        parameters = {"token": self.user_token,
                      "container_id": self.c1,
                      "container_path": "/foo",
                      "host_path": "/foo",
                      "host_to_container": False}
        body = request.make_body(parameters)
        result = webob.Request.blank("/copy",
                                     content_type="application/json",
                                     body=body,
                                     method="PUT").get_response(self.app)
        self.assertEqual(201, result.status_code)
        self.assertEqual(stat, result.json_body["results"])
