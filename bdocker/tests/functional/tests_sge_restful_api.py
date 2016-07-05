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

import copy
import docker as docker_py
import json
import os
import uuid

from cgroupspy import nodes
import mock
import testtools
import webob

from bdocker.modules import request
from bdocker.tests.functional import fakes


def create_fake_json_resp(data, status=200):
    r = webob.Response()
    r.headers["Content-Type"] = "application/json"
    r.charset = "utf8"
    r.body = json.dumps(data).encode("utf8")
    r.status_code = status
    return r


class TestSgeRestApiAccounting(testtools.TestCase):
    """Tests the all workflow of REST API methods
    for Accounting."""
    def setUp(self):
        super(TestSgeRestApiAccounting, self).setUp()
        self.admin_token = fakes.admin_token
        self.user_token = fakes.user_token
        self.app = fakes.create_accounting_app()

    @mock.patch("__builtin__.open")
    def test_set_job(self, m_file):
        line = (
            "docker:ge-wn03.novalocal:hpc:"
            "jorgesece:bdocker_job.sh.o80:81:sge:15:"
            "1465486337:1465486332:1465486332:0:127:"
            "0:0.053201:0.100611:5632.000000:0:0:0:"
            "0:25024:0:0:0.000000:72:0:0:0:242:55:"
            "NONE:sysusers:NONE:1:0:0.000000:0.000000:"
            "0.000000:-U sysusers:0.000000:"
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


class TestSgeRestApiWn(testtools.TestCase):
    """Tests the all workflow of REST API methods
     for WN."""

    def setUp(self):
        super(TestSgeRestApiWn, self).setUp()
        file_name = os.path.join(os.path.dirname(__file__),
                                 'sge_wn_configure.cfg')
        self.app = fakes.create_working_node_app(file_name)
        self.token_store = copy.copy(fakes.token_store)
        self.admin_token = self.token_store["prolog"]["token"]

    @mock.patch("pwd.getpwuid")
    @mock.patch("os.path.realpath")
    @mock.patch("bdocker.utils.write_yaml_file")
    @mock.patch("bdocker.utils.read_yaml_file")
    @mock.patch("bdocker.utils.read_file")
    @mock.patch.object(nodes.Node, "create_cgroup")
    @mock.patch("os.fork")
    @mock.patch("bdocker.utils.update_yaml_file")
    @mock.patch("os.setsid")
    @mock.patch("os.kill")
    @mock.patch("time.sleep")
    def test_configuration(self, m_time, m_kill,
                           m_setsid, m_up, m_fork,
                           m_cre, m_r, m_ry, m_w,
                           m_path, m_getpi):
        cpu_usage = 5
        cpu_max = 1
        memory_usage = 1
        memory_max = 5
        job_pid = 33
        user_home = "/baa"
        user_gid = uuid.uuid4().hex
        user_gid = uuid.uuid4().hex
        parameters = {"admin_token": fakes.admin_token,
                      "user_credentials":
                          {'uid': user_gid,
                           'gid': user_gid,
                           "home": user_home,
                           'job': {'job_id': 2,
                                   'spool': '/faa',
                                   "max_cpu": cpu_max,
                                   "max_memory": memory_max,
                                   "user_name": "",
                                   "queue_name": "",
                                   "host_name": "",
                                   "job_name": "",
                                   "account_name": "",
                                   "log_name": ""}
                           }
                      }
        m_r.side_effect = [None, memory_usage,
                           cpu_usage, job_pid]
        m_fork.return_value = 0
        m_ry.return_value = self.token_store
        user_token_conf = uuid.uuid4().hex
        mock_uid = mock.MagicMock()
        mock_uid.hex = user_token_conf
        m_class = mock.MagicMock()
        m_class.pw_gid = user_gid
        m_getpi.return_value = m_class
        m_path.return_value = user_home
        body = request.make_body(parameters)
        with mock.patch.object(uuid, "uuid4", return_value=mock_uid):
            result = webob.Request.blank("/configuration",
                                         method="POST",
                                         content_type="application/json",
                                         body=body).get_response(self.app)
        self.assertEqual(201, result.status_code)
        self.assertEqual(user_token_conf,
                         result.json_body["results"])
        self.assertIn(user_token_conf, self.token_store)
        self.assertEqual(2, m_kill.call_count)

    @mock.patch.object(nodes.Node, "delete_cgroup")
    @mock.patch("bdocker.utils.read_file")
    @mock.patch("bdocker.utils.add_to_file")
    @mock.patch("bdocker.utils.delete_file")
    @mock.patch("bdocker.utils.read_yaml_file")
    @mock.patch("bdocker.utils.write_yaml_file")
    @mock.patch.object(request.RequestController, "_get_req")
    @mock.patch.object(docker_py.Client, "remove_container")
    def test_clean(self, m_dock, m_rq, m_w, m_ry,
                   m_del, m_add, m_r, m_delgroup):
        token = fakes.user_token_clean
        out = create_fake_json_resp(
            {}, 204)
        m_rq.return_value.get_response.return_value = out
        m_r.return_value = "2222\n3333"
        m_ry.side_effect = [
            self.token_store[token]['job'],
            self.token_store
        ]
        parameters = {"admin_token": fakes.admin_token,
                      "token": token}
        query = request.get_query_string(parameters)
        result = webob.Request.blank(
            "/clean?%s" % query,
            method="DELETE",
            content_type="application/json"
        ).get_response(self.app)
        self.assertEqual(204, result.status_code)
        self.assertNotIn(token,
                         self.token_store)

    @mock.patch.object(docker_py.Client, "pull")
    def test_pull(self, m_pull):
        token = fakes.user_token
        image_id_1 = uuid.uuid4().hex
        image_id_2 = uuid.uuid4().hex
        logs = [{
            "status": "Pulling image (latest) from busybox",
            "progressDetail": {},
            "id": image_id_1
        },
            {
                "status": "Pulling image (latest) from busybox",
                "progressDetail": {},
                "id": image_id_2
            }]

        def create_log():
            for l in logs:
                yield(json.dumps(l))
        m_pull.return_value = create_log()
        parameters = {"token": token,
                      "source": 'repoooo'}
        body = request.make_body(parameters)
        result = webob.Request.blank("/pull",
                                     content_type="application/json",
                                     body=body,
                                     method="POST").get_response(self.app)
        self.assertEqual(201, result.status_code)
        self.assertIn(image_id_1, result.json_body["results"][0])
        self.assertIn(image_id_2, result.json_body["results"][1])

    @mock.patch.object(docker_py.Client, "remove_container")
    @mock.patch("bdocker.utils.write_yaml_file")
    @mock.patch("bdocker.utils.read_yaml_file")
    def test_delete(self, m_r, m_w, md):
        token = fakes.user_token_delete
        m_r.return_value = self.token_store
        force = False
        containers = copy.copy(
            self.token_store[token]["containers"]
        )
        parameters = {
            "token": token,
            "container_id": containers,
            "force": force}
        body = request.make_body(parameters)
        result = webob.Request.blank("/rm",
                                     content_type="application/json",
                                     body=body,
                                     method="PUT").get_response(self.app)
        self.assertEqual(200, result.status_code)
        self.assertEqual(containers[0], result.json_body["results"][0])
        self.assertEqual(containers[1], result.json_body["results"][1])
        self.assertNotIn("containers",
                         self.token_store[token])

    @mock.patch.object(docker_py.Client, "containers")
    def test_ps(self, ml):
        token = fakes.user_token
        containers = self.token_store[token]["containers"]
        ml.return_value = [
            {"Id": containers[0],
             "Created": 666.777,
             "Names": ["y"],
             "Ports":["z"],
             "Image": "image_name",
             "Command": "ls",
             "Status": "status"},
            {"Id": containers[1],
             "Created": 666.777,
             "Names": ["y"],
             "Ports":["z"],
             "Image": "image_name",
             "Command": "ls",
             "Status": "status"}]

        all = True
        result = webob.Request.blank("/ps?token=%s&all=%s" % (token, all),
                                     method="GET").get_response(self.app)
        self.assertEqual(200, result.status_code)
        self.assertIn(result.json_body["results"][0][0], containers[0])
        self.assertIn(result.json_body["results"][1][0], containers[1])

    @mock.patch.object(docker_py.Client, "inspect_container")
    def test_show(self, md):
        token = fakes.user_token
        containers = self.token_store[token]["containers"]
        parameters = {"token": token,
                      "container_id": containers[0]}
        md.return_value = fake_out = {
            "containerId": containers[0],
            "command": "ls"
        }
        query = request.get_query_string(parameters)
        result = webob.Request.blank("/inspect?%s" % query,
                                     method="GET").get_response(self.app)
        self.assertEqual(200, result.status_code)
        self.assertIsNotNone(json.loads(result.json_body["results"])[0])
        out = json.loads(result.json_body["results"])[0]
        self.assertEqual(fake_out["containerId"], out["containerId"])
        self.assertEqual(fake_out["command"], out["command"])

    @mock.patch.object(docker_py.Client, "logs")
    def test_logs(self, m_logs):
        token = fakes.user_token
        containers = self.token_store[token]["containers"]
        logs = [uuid.uuid4().hex, uuid.uuid4().hex]

        def create_log():
            for l in logs:
                yield(l)
        m_logs.return_value = create_log()
        parameters = {"token": token,
                      "container_id": containers[0]}
        query = request.get_query_string(parameters)
        result = webob.Request.blank("/logs?%s" % query,
                                     method="GET").get_response(self.app)
        self.assertEqual(200, result.status_code)
        self.assertEqual(logs, result.json_body["results"])

    @mock.patch.object(docker_py.Client, "stop")
    def test_stop(self, md):
        token = fakes.user_token
        containers = self.token_store[token]["containers"]
        parameters = {"token": token,
                      "container_id": containers[0]}
        body = request.make_body(parameters)
        result = webob.Request.blank("/stop",
                                     content_type="application/json",
                                     body=body,
                                     method="POST").get_response(self.app)
        self.assertEqual(200, result.status_code)

    @mock.patch.object(docker_py.Client, "put_archive")
    @mock.patch("bdocker.utils.read_tar_raw_data_stream")
    def test_cp_to_container(self, m_str, m_put):
        token = fakes.user_token
        containers = self.token_store[token]["containers"]
        user_home = self.token_store[token]["home"]
        m_put.return_value = True
        parameters = {"token": token,
                      "container_id": containers[0],
                      "container_path": "/coo",
                      "host_path": user_home,
                      "host_to_container": True}
        body = request.make_body(parameters)
        result = webob.Request.blank("/copy",
                                     content_type="application/json",
                                     body=body,
                                     method="PUT").get_response(self.app)
        self.assertEqual(201, result.status_code)
        self.assertEqual(True, result.json_body["results"])

    @mock.patch.object(docker_py.Client, "get_archive")
    @mock.patch("bdocker.utils.write_tar_raw_data_stream")
    def test_cp_from_container(self, m_str, m_g):
        token = fakes.user_token
        containers = self.token_store[token]["containers"]
        user_home = self.token_store[token]["home"]
        out = mock.MagicMock()
        out.data = None
        stat = {'linkTarget': '',
                'mode': 493,
                'mtime': '2015-09-16T12:34:23-07:00',
                'name': 'sh',
                'size': 962860
                }
        m_g.return_value = out, stat
        parameters = {"token": token,
                      "container_id": containers[0],
                      "container_path": "/coo",
                      "host_path": user_home,
                      "host_to_container": False}
        body = request.make_body(parameters)
        result = webob.Request.blank("/copy",
                                     content_type="application/json",
                                     body=body,
                                     method="PUT").get_response(self.app)
        self.assertEqual(201, result.status_code)
        self.assertEqual(stat, result.json_body["results"])

    @mock.patch.object(docker_py.Client, "create_container")
    @mock.patch.object(docker_py.Client, "start")
    @mock.patch.object(docker_py.Client, "logs")
    @mock.patch("bdocker.utils.write_yaml_file")
    @mock.patch("bdocker.utils.read_yaml_file")
    def test_run(self, m_r, m_w, m_log, m_start, m_cre):
        logs = [uuid.uuid4().hex, uuid.uuid4().hex]

        def create_log():
            for l in logs:
                yield(l)
        m_log.return_value = create_log()

        token = fakes.user_token
        user_home = self.token_store[token]["home"]
        m_r.return_value = self.token_store
        image_id = uuid.uuid4().hex
        container_id = uuid.uuid4().hex
        script = 'ls'
        detach = False
        m_cre.return_value = {'Id': container_id}
        parameters = {"token": token,
                      "image_id": image_id,
                      "script": script,
                      "detach": detach,
                      "host_dir": user_home,
                      "docker_dir": "/doo",
                      "working_dir": "/doo",
                      }
        body = request.make_body(parameters)
        result = webob.Request.blank("/run",
                                     content_type="application/json",
                                     body=body,
                                     method="PUT").get_response(self.app)
        self.assertEqual(201, result.status_code)
        self.assertEqual(True, m_log.called)
        self.assertEqual(True, m_start.called)
        self.assertEqual(True, m_cre.called)
        self.assertIn(container_id, self.token_store[token]["containers"])
        self.assertEqual(logs, result.json_body["results"])

    @mock.patch.object(docker_py.Client, "create_container")
    @mock.patch.object(docker_py.Client, "start")
    @mock.patch.object(docker_py.Client, "logs")
    @mock.patch("bdocker.utils.write_yaml_file")
    @mock.patch("bdocker.utils.read_yaml_file")
    def test_run_detach(self, m_r, m_w, m_log, m_start, m_cre):
        m_r.return_value = self.token_store
        token = fakes.user_token
        user_home = self.token_store[token]["home"]
        image_id = uuid.uuid4().hex
        container_id = uuid.uuid4().hex
        script = 'ls'
        detach = True
        m_cre.return_value = {'Id': container_id}
        parameters = {"token": token,
                      "image_id": image_id,
                      "script": script,
                      "detach": detach,
                      "host_dir": user_home,
                      "docker_dir": "/doo",
                      "working_dir": "/doo",
                      }
        body = request.make_body(parameters)
        result = webob.Request.blank("/run",
                                     content_type="application/json",
                                     body=body,
                                     method="PUT").get_response(self.app)
        self.assertEqual(201, result.status_code)
        self.assertEqual(False, m_log.called)
        self.assertEqual(True, m_start.called)
        self.assertEqual(True, m_cre.called)
        self.assertIn(container_id, self.token_store[token]["containers"])
        self.assertEqual(container_id, result.json_body["results"])
