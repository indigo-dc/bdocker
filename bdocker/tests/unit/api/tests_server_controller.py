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

from bdocker.api import controller
from bdocker import exceptions


class TestAccountingServerController(testtools.TestCase):
    """Test Server Controller class."""

    def setUp(self):
        super(TestAccountingServerController, self).setUp()

    @mock.patch("bdocker.modules.load_credentials_module")
    @mock.patch("bdocker.modules.load_batch_module")
    def test_set_job_accounting(self, m_batch, m_cre):
        token = uuid.uuid4().hex
        accounting = uuid.uuid4().hex
        expected = uuid.uuid4().hex
        m_class = mock.MagicMock()
        m_class.set_job_accounting.return_value = expected
        m_batch.return_value = m_class
        contr = controller.AccountingServerController(None)
        data = {'admin_token': token,
                'accounting': accounting}

        result = contr.set_job_accounting(data)

        self.assertEqual(expected, result)


class TestServerController(testtools.TestCase):
    """Test Server Controller class."""

    def setUp(self):
        super(TestServerController, self).setUp()

    @mock.patch("bdocker.modules.load_credentials_module")
    @mock.patch("bdocker.modules.load_batch_module")
    @mock.patch("bdocker.modules.load_docker_module")
    def test_configuration(self, m_dock, m_batch, m_cre):
        token = uuid.uuid4().hex
        m_class_cre = mock.MagicMock()
        m_class_cre.authenticate.return_value = token
        m_cre.return_value = m_class_cre
        contr = controller.ServerController(None)
        data = {"admin_token": uuid.uuid4().hex,
                "user_credentials": {"job": {
                    "id": uuid.uuid4().hex,
                    "spool": "/foo"
                }}
                }
        result = contr.configuration(data)

        self.assertEqual(token, result)

    @mock.patch("bdocker.modules.load_credentials_module")
    @mock.patch("bdocker.modules.load_batch_module")
    @mock.patch("bdocker.modules.load_docker_module")
    def test_pull(self, m_dock, m_batch, m_cre):
        m_class_dock = mock.MagicMock()
        im_id = uuid.uuid4().hex
        m_class_dock.pull_image.return_value = im_id
        m_dock.return_value = m_class_dock
        contr = controller.ServerController(None)
        parameters = {"token": "tokennnnnn",
                      "source": 'repoooo'}
        result = contr.pull(parameters)
        self.assertEqual(im_id, result)

    @mock.patch("bdocker.modules.load_credentials_module")
    @mock.patch("bdocker.modules.load_batch_module")
    @mock.patch("bdocker.modules.load_docker_module")
    def test_pull_unauthorized(self, m_dock, m_batch, m_cre):
        expected = exceptions.UserCredentialsException("")
        m_class_cre = mock.MagicMock()
        m_class_cre.authorize.side_effect = expected
        m_cre.return_value = m_class_cre
        contr = controller.ServerController(None)
        parameters = {"token": "tokennnnnn",
                      "source": 'repoooo'}
        self.assertRaises(exceptions.UserCredentialsException,
                          contr.pull,
                          parameters)

    @mock.patch("bdocker.modules.load_credentials_module")
    @mock.patch("bdocker.modules.load_batch_module")
    @mock.patch("bdocker.modules.load_docker_module")
    def test_list(self, m_dock, m_batch, m_cre):
        c1 = uuid.uuid4().hex
        c2 = uuid.uuid4().hex
        c3 = uuid.uuid4().hex
        containers = [c1, c2, c3]
        m_class_cre = mock.MagicMock()
        m_class_cre.list_containers.return_value = containers
        m_cre.return_value = m_class_cre
        info_containers = [{"info"}, {"info"}]
        m_class_dock = mock.MagicMock()
        m_class_dock.list_containers.return_value = info_containers
        m_dock.return_value = m_class_dock
        contr = controller.ServerController(None)
        parameters = {"token": uuid.uuid4().hex}
        results = contr.list_containers(parameters)
        self.assertEqual(results.__len__(), info_containers.__len__())

    @mock.patch("bdocker.modules.load_credentials_module")
    @mock.patch("bdocker.modules.load_batch_module")
    @mock.patch("bdocker.modules.load_docker_module")
    def test_list_empty(self, m_dock, m_batch, m_cre):
        containers = []
        m_class_cre = mock.MagicMock()
        m_class_cre.list_containers.return_value = containers
        m_cre.return_value = m_class_cre
        contr = controller.ServerController(None)
        parameters = {"token": uuid.uuid4().hex}
        results = contr.list_containers(parameters)
        self.assertEqual([], results)

    @mock.patch("bdocker.modules.load_credentials_module")
    @mock.patch("bdocker.modules.load_batch_module")
    @mock.patch("bdocker.modules.load_docker_module")
    def test_list_unauthorized(self, m_dock, m_batch, m_cre):
        expected = exceptions.UserCredentialsException("")
        m_class_cre = mock.MagicMock()
        m_class_cre.list_containers.side_effect = expected
        m_cre.return_value = m_class_cre
        contr = controller.ServerController(None)
        parameters = {"token": uuid.uuid4().hex}
        self.assertRaises(exceptions.UserCredentialsException,
                          contr.list_containers,
                          parameters)

    @mock.patch("bdocker.modules.load_credentials_module")
    @mock.patch("bdocker.modules.load_batch_module")
    @mock.patch("bdocker.modules.load_docker_module")
    def test_show(self, m_dock, m_batch, m_cre):
        c1 = uuid.uuid4().hex
        m_class_cre = mock.MagicMock()
        m_class_cre.authorize_container.return_value = c1
        m_cre.return_value = m_class_cre
        info_containers = {"info"}
        m_class_dock = mock.MagicMock()
        m_class_dock.container_details.return_value = info_containers
        m_dock.return_value = m_class_dock
        contr = controller.ServerController(None)
        parameters = {"token": uuid.uuid4().hex,
                      "container_id": c1}
        results = contr.show(parameters)
        self.assertEqual(info_containers, results)

    @mock.patch("bdocker.modules.load_credentials_module")
    @mock.patch("bdocker.modules.load_batch_module")
    @mock.patch("bdocker.modules.load_docker_module")
    def test_show_unauthorized(self, m_dock, m_batch, m_cre):
        expected = exceptions.UserCredentialsException("")
        m_class_cre = mock.MagicMock()
        m_class_cre.authorize_container.side_effect = expected
        m_cre.return_value = m_class_cre
        contr = controller.ServerController(None)
        parameters = {"token": uuid.uuid4().hex,
                      "container_id": uuid.uuid4().hex}
        self.assertRaises(exceptions.UserCredentialsException,
                          contr.show,
                          parameters)

    @mock.patch("bdocker.modules.load_credentials_module")
    @mock.patch("bdocker.modules.load_batch_module")
    @mock.patch("bdocker.modules.load_docker_module")
    def test_logs(self, m_dock, m_batch, m_cre):
        c1 = uuid.uuid4().hex
        m_class_cre = mock.MagicMock()
        m_class_cre.authorize_container.return_value = c1
        m_cre.return_value = m_class_cre
        info_containers = {"info"}
        m_class_dock = mock.MagicMock()
        m_class_dock.logs_container.return_value = info_containers
        m_dock.return_value = m_class_dock
        contr = controller.ServerController(None)
        parameters = {"token": uuid.uuid4().hex,
                      "container_id": c1}
        results = contr.logs(parameters)
        self.assertEqual(info_containers, results)

    @mock.patch("bdocker.modules.load_credentials_module")
    @mock.patch("bdocker.modules.load_batch_module")
    @mock.patch("bdocker.modules.load_docker_module")
    def test_log_unauthorized(self, m_dock, m_batch, m_cre):
        c1 = uuid.uuid4().hex
        expected = exceptions.UserCredentialsException("")
        m_class_cre = mock.MagicMock()
        m_class_cre.authorize_container.side_effect = expected
        m_cre.return_value = m_class_cre
        contr = controller.ServerController(None)
        parameters = {"token": uuid.uuid4().hex,
                      "container_id": c1}
        self.assertRaises(exceptions.UserCredentialsException,
                          contr.logs,
                          parameters)

    @mock.patch("bdocker.modules.load_credentials_module")
    @mock.patch("bdocker.modules.load_batch_module")
    @mock.patch("bdocker.modules.load_docker_module")
    def test_delete(self, m_dock, m_batch, m_cre):
        c1 = uuid.uuid4().hex
        m_class_cre = mock.MagicMock()
        m_class_cre.authorize_container.return_value = c1
        m_cre.return_value = m_class_cre
        contr = controller.ServerController(None)
        parameters = {"token": uuid.uuid4().hex,
                      "container_id": c1}
        results = contr.delete_container(parameters)
        self.assertEqual([c1], results)

    @mock.patch("bdocker.modules.load_credentials_module")
    @mock.patch("bdocker.modules.load_batch_module")
    @mock.patch("bdocker.modules.load_docker_module")
    def test_delete_force(self, m_dock, m_batch, m_cre):
        c1 = uuid.uuid4().hex
        m_class_cre = mock.MagicMock()
        m_class_cre.authorize_container.return_value = c1
        m_cre.return_value = m_class_cre
        contr = controller.ServerController(None)
        force = True
        parameters = {"token": uuid.uuid4().hex,
                      "container_id": c1,
                      "force": force}
        results = contr.delete_container(parameters)
        self.assertEqual([c1], results)
        self.assertEqual(force, m_dock.mock_calls[1][1][1])
        self.assertEqual(c1, m_dock.mock_calls[1][1][0])

    @mock.patch("bdocker.modules.load_credentials_module")
    @mock.patch("bdocker.modules.load_batch_module")
    @mock.patch("bdocker.modules.load_docker_module")
    def test_delete_several(self, m_dock, m_batch, m_cre):
        c1 = uuid.uuid4().hex
        c2 = uuid.uuid4().hex
        m_class_cre = mock.MagicMock()
        m_class_cre.authorize_container.side_effect = [c1, c2]
        m_cre.return_value = m_class_cre
        contr = controller.ServerController(None)
        parameters = {"token": uuid.uuid4().hex,
                      "container_id": [c1, c2]}
        results = contr.delete_container(parameters)
        self.assertEqual([c1, c2], results)

    @mock.patch("bdocker.modules.load_credentials_module")
    @mock.patch("bdocker.modules.load_batch_module")
    @mock.patch("bdocker.modules.load_docker_module")
    def test_delete_unauthorized(self, m_dock, m_batch, m_cre):
        c1 = uuid.uuid4().hex
        expected = exceptions.UserCredentialsException("")
        m_class_cre = mock.MagicMock()
        m_class_cre.authorize_container.side_effect = expected
        m_cre.return_value = m_class_cre
        contr = controller.ServerController(None)
        parameters = {"token": uuid.uuid4().hex,
                      "container_id": c1}
        results = contr.delete_container(parameters)
        self.assertEqual(1, results.__len__())
        self.assertIn("Exception", results[0])

    @mock.patch("bdocker.modules.load_credentials_module")
    @mock.patch("bdocker.modules.load_batch_module")
    @mock.patch("bdocker.modules.load_docker_module")
    def test_delete_several_unauthorized(self, m_dock, m_batch, m_cre):
        c1 = uuid.uuid4().hex
        c2 = uuid.uuid4().hex
        c3 = uuid.uuid4().hex
        expected = [exceptions.UserCredentialsException(""),
                    c2,
                    c3]
        m_class_cre = mock.MagicMock()
        m_class_cre.authorize_container.side_effect = expected
        m_cre.return_value = m_class_cre
        contr = controller.ServerController(None)
        parameters = {"token": uuid.uuid4().hex,
                      "container_id": [c1, c2, c3]}
        results = contr.delete_container(parameters)
        self.assertEqual(3, results.__len__())
        self.assertIn("Exception", results[0])
        self.assertEqual(c2, results[1])
        self.assertEqual(c3, results[2])

    @mock.patch("bdocker.modules.load_credentials_module")
    @mock.patch("bdocker.modules.load_batch_module")
    @mock.patch("bdocker.modules.load_docker_module")
    def test_run_full(self, m_dock, m_batch, m_cre):
        m_class_cre = mock.MagicMock()
        cgroup = uuid.uuid4().hex
        expected_job = {"cgroup": cgroup}
        m_class_cre.get_job_from_token.return_value = expected_job
        log_info = "logsssss"
        m_cre.return_value = m_class_cre
        container_id = uuid.uuid4().hex
        m_class_dock = mock.MagicMock()
        m_class_dock.run_container.return_value = container_id
        m_class_dock.logs_container.return_value = log_info
        m_dock.return_value = m_class_dock
        contr = controller.ServerController(None)
        token = uuid.uuid4().hex
        image_id = uuid.uuid4().hex
        log_info = "logsssss"
        script = 'ls'
        detach = False
        host_dir = "/foo"
        docker_dir = "/foo"
        working_dir = "/foo"
        parameters = {"token": token,
                      "image_id": image_id,
                      "script": script,
                      "detach": detach,
                      "host_dir": host_dir,
                      "docker_dir": docker_dir,
                      "working_dir": working_dir
                      }
        results = contr.run(parameters)
        self.assertEqual(log_info, results)
        self.assertEqual((token, host_dir), m_cre.mock_calls[1][1])
        expected_run_call = (image_id,
                             detach,
                             script)

        expected_run_dict = {
            "host_dir": host_dir,
            "docker_dir": docker_dir,
            "working_dir": working_dir,
            "cgroup": cgroup
        }
        self.assertEqual(expected_run_call,
                         m_dock.mock_calls[1][1])
        self.assertEqual(expected_run_dict,
                         m_dock.mock_calls[1][2])
        self.assertEqual((token, container_id), m_cre.mock_calls[3][1])
        self.assertIn(container_id,
                      m_dock.mock_calls[2][1])
        self.assertIn(container_id,
                      m_dock.mock_calls[3][1])

    @mock.patch("bdocker.modules.load_credentials_module")
    @mock.patch("bdocker.modules.load_batch_module")
    @mock.patch("bdocker.modules.load_docker_module")
    def test_run_no_host_dir(self, m_dock, m_batch, m_cre):
        m_class_cre = mock.MagicMock()
        cgroup = uuid.uuid4().hex
        expected_job = {"cgroup": cgroup}
        m_class_cre.get_job_from_token.return_value = expected_job
        log_info = "logsssss"
        m_cre.return_value = m_class_cre
        container_id = uuid.uuid4().hex
        m_class_dock = mock.MagicMock()
        m_class_dock.run_container.return_value = container_id
        m_class_dock = mock.MagicMock()
        m_class_dock.run_container.return_value = container_id
        m_class_dock.logs_container.return_value = log_info
        m_dock.return_value = m_class_dock
        token = uuid.uuid4().hex
        image_id = uuid.uuid4().hex
        script = 'ls'
        detach = False
        host_dir = None
        docker_dir = "/foo"
        working_dir = "/foo"
        parameters = {"token": token,
                      "image_id": image_id,
                      "script": script,
                      "detach": detach,
                      "host_dir": host_dir,
                      "docker_dir": docker_dir,
                      "working_dir": working_dir
                      }
        contr = controller.ServerController(None)
        results = contr.run(parameters)
        self.assertEqual(log_info, results)
        self.assertNotIn('().authorize_directory', m_cre.mock_calls[1])

    @mock.patch("bdocker.modules.load_credentials_module")
    @mock.patch("bdocker.modules.load_batch_module")
    @mock.patch("bdocker.modules.load_docker_module")
    def test_run_detach(self, m_dock, m_batch, m_cre):
        m_class_cre = mock.MagicMock()
        cgroup = uuid.uuid4().hex
        expected_job = {"cgroup": cgroup}
        m_class_cre.get_job_from_token.return_value = expected_job
        log_info = "logsssss"
        m_cre.return_value = m_class_cre
        container_id = uuid.uuid4().hex
        m_class_dock = mock.MagicMock()
        m_class_dock.run_container.return_value = container_id
        m_class_dock.logs_container.return_value = log_info
        m_dock.return_value = m_class_dock
        contr = controller.ServerController(None)
        token = uuid.uuid4().hex
        image_id = uuid.uuid4().hex
        script = 'ls'
        detach = True
        host_dir = None
        docker_dir = "/foo"
        working_dir = "/foo"
        parameters = {"token": token,
                      "image_id": image_id,
                      "script": script,
                      "detach": detach,
                      "host_dir": host_dir,
                      "docker_dir": docker_dir,
                      "working_dir": working_dir
                      }
        results = contr.run(parameters)
        self.assertEqual(container_id, results)

    @mock.patch("bdocker.modules.load_credentials_module")
    @mock.patch("bdocker.modules.load_batch_module")
    @mock.patch("bdocker.modules.load_docker_module")
    def test_run_unautorized(self, m_dock, m_batch, m_cre):
        expected = exceptions.UserCredentialsException("")
        m_class_cre = mock.MagicMock()
        m_class_cre.authorize_directory.side_effect = expected
        m_cre.return_value = m_class_cre
        contr = controller.ServerController(None)
        token = uuid.uuid4().hex
        image_id = uuid.uuid4().hex
        script = 'ls'
        detach = True
        host_dir = "/foo"
        docker_dir = "/foo"
        working_dir = "/foo"
        parameters = {"token": token,
                      "image_id": image_id,
                      "script": script,
                      "detach": detach,
                      "host_dir": host_dir,
                      "docker_dir": docker_dir,
                      "working_dir": working_dir
                      }
        self.assertRaises(exceptions.UserCredentialsException,
                          contr.run,
                          parameters)

    @mock.patch("bdocker.modules.load_credentials_module")
    @mock.patch("bdocker.modules.load_batch_module")
    @mock.patch("bdocker.modules.load_docker_module")
    def test_notify_accounting(self, m_dock, m_batch, m_cre):
        expected = uuid.uuid4().hex
        m_class_batch = mock.MagicMock()
        m_class_batch.notify_accounting.return_value = expected
        m_batch.return_value = m_class_batch
        parameters = {"token": uuid.uuid4().hex,
                      'admin_token': uuid.uuid4().hex}
        contr = controller.ServerController(None)
        results = contr.notify_accounting(parameters)
        self.assertEqual(expected, results)

    @mock.patch("bdocker.modules.load_credentials_module")
    @mock.patch("bdocker.modules.load_batch_module")
    @mock.patch("bdocker.modules.load_docker_module")
    def test_notify_accounting_unauthorized(self, m_dock, m_batch, m_cre):
        expected = exceptions.UserCredentialsException("")
        m_class_cre = mock.MagicMock()
        m_class_cre.authorize_admin.side_effect = expected
        m_cre.return_value = m_class_cre
        contr = controller.ServerController(None)
        parameters = {"token": uuid.uuid4().hex,
                      'admin_token': uuid.uuid4().hex}
        self.assertRaises(exceptions.UserCredentialsException,
                          contr.notify_accounting,
                          parameters)

    @mock.patch("bdocker.modules.load_credentials_module")
    @mock.patch("bdocker.modules.load_batch_module")
    @mock.patch("bdocker.modules.load_docker_module")
    def test_stop(self, m_dock, m_batch, m_cre):
        c1 = uuid.uuid4().hex
        info_containers = {"info"}
        m_class_dock = mock.MagicMock()
        m_class_dock.stop_container.return_value = info_containers
        m_dock.return_value = m_class_dock
        contr = controller.ServerController(None)
        parameters = {"token": uuid.uuid4().hex,
                      "container_id": c1}
        results = contr.stop_container(parameters)
        self.assertEqual(info_containers, results)

    @mock.patch("bdocker.modules.load_credentials_module")
    @mock.patch("bdocker.modules.load_batch_module")
    @mock.patch("bdocker.modules.load_docker_module")
    def test_stop_unauthorized(self, m_dock, m_batch, m_cre):
        c1 = uuid.uuid4().hex
        expected = exceptions.UserCredentialsException("")
        m_class_cre = mock.MagicMock()
        m_class_cre.authorize_container.side_effect = expected
        m_cre.return_value = m_class_cre
        contr = controller.ServerController(None)
        parameters = {"token": uuid.uuid4().hex,
                      "container_id": c1}
        self.assertRaises(exceptions.UserCredentialsException,
                          contr.stop_container,
                          parameters)

    @mock.patch("bdocker.modules.load_credentials_module")
    @mock.patch("bdocker.modules.load_batch_module")
    @mock.patch("bdocker.modules.load_docker_module")
    def test_copy_to_container(self, m_dock, m_batch, m_cre):
        c1 = uuid.uuid4().hex
        info_containers = {"info"}
        m_class_dock = mock.MagicMock()
        m_class_dock.copy_to_container.return_value = info_containers
        m_dock.return_value = m_class_dock
        contr = controller.ServerController(None)
        parameters = {"token": uuid.uuid4().hex,
                      "container_id": c1,
                      "container_path": "/foo",
                      "host_path": "/foo",
                      "host_to_container": True}
        results = contr.copy(parameters)
        self.assertNotIn('().copy_from_container', m_dock.mock_calls[1])
        self.assertIn('().copy_to_container', m_dock.mock_calls[1])
        self.assertEqual(info_containers, results)

    @mock.patch("bdocker.modules.load_credentials_module")
    @mock.patch("bdocker.modules.load_batch_module")
    @mock.patch("bdocker.modules.load_docker_module")
    def test_copy_from_container(self, m_dock, m_batch, m_cre):
        c1 = uuid.uuid4().hex
        info_containers = {"info"}
        m_class_dock = mock.MagicMock()
        m_class_dock.copy_from_container.return_value = info_containers
        m_dock.return_value = m_class_dock
        contr = controller.ServerController(None)
        parameters = {"token": uuid.uuid4().hex,
                      "container_id": c1,
                      "container_path": "/foo",
                      "host_path": "/foo",
                      "host_to_container": False}
        results = contr.copy(parameters)
        self.assertIn('().copy_from_container', m_dock.mock_calls[1])
        self.assertNotIn('().copy_to_container', m_dock.mock_calls[1])
        self.assertEqual(info_containers, results)

    @mock.patch("bdocker.modules.load_credentials_module")
    @mock.patch("bdocker.modules.load_batch_module")
    @mock.patch("bdocker.modules.load_docker_module")
    def test_copy_unauthorized(self, m_dock, m_batch, m_cre):
        c1 = uuid.uuid4().hex
        expected = exceptions.UserCredentialsException("")
        m_class_cre = mock.MagicMock()
        m_class_cre.authorize_container.side_effect = expected
        m_cre.return_value = m_class_cre
        contr = controller.ServerController(None)
        parameters = {"token": uuid.uuid4().hex,
                      "container_id": c1,
                      "container_path": "/foo",
                      "host_path": "/foo",
                      "host_to_container": True}
        self.assertRaises(exceptions.UserCredentialsException,
                          contr.copy,
                          parameters)
