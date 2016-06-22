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

import uuid
import testtools

import mock

from bdocker.common.modules import credentials
from bdocker.common.modules import docker_helper
from bdocker.common.modules import batch
from bdocker.common import utils
from bdocker.common import exceptions
from bdocker.server import controller

FAKE_CONF = {
    'server': mock.MagicMock(),
    'batch': mock.MagicMock(),
    'credentials': mock.MagicMock(),
    'dockerAPI': mock.MagicMock(),
}


class TestAccountingServerController(testtools.TestCase):
    """Test Server Controller class."""

    def setUp(self):
        super(TestAccountingServerController, self).setUp()
        path = ("/home/jorge/Dropbox/INDIGO_DOCKER/"
                "bdocker/bdocker/common/"
                "configure_bdocker_accounting.cfg")
        # TODO(jorgesece): create a fake conf without need a file
        conf = utils.load_configuration_from_file(path)
        self.controller = controller.AccountingServerController(conf)

    @mock.patch.object(credentials.UserController, "authorize_admin")
    @mock.patch.object(batch.SGEAccountingController, "set_job_accounting")
    def test_set_job_accounting(self, m, m_au):
        token = uuid.uuid4().hex
        accounting = uuid.uuid4().hex
        m_au.return_value = token
        expected = uuid.uuid4().hex
        m.return_value = expected
        data = {'admin_token': token,
                'accounting': accounting}

        result = self.controller.set_job_accounting(data)

        self.assertEqual(expected, result)



class TestServerController(testtools.TestCase):
    """Test Server Controller class."""

    def setUp(self):
        super(TestServerController, self).setUp()
        path = "/home/jorge/Dropbox/INDIGO_DOCKER/" \
                                          "bdocker/bdocker/common/" \
                                          "configure_bdocker.cfg"
        # TODO(jorgesece): create a fake conf without need a file
        conf = utils.load_configuration_from_file(path)
        self.controller = controller.ServerController(conf)

    @mock.patch.object(credentials.UserController, "authenticate")
    @mock.patch.object(credentials.UserController, "set_token_batch_info")
    @mock.patch.object(batch.SGEController, "conf_environment")
    def test_configuration(self, m_conf, m_t, m_au):
        token = uuid.uuid4().hex
        m_au.return_value = token
        data = {"admin_token": "tokennnnnn",
                "user_credentials": {"job":{
                    "id": uuid.uuid4().hex,
                    "spool": "/foo"
                }}
                }
        result = self.controller.configuration(data)

        self.assertEqual(token, result)

    @mock.patch.object(docker_helper.DockerController, "pull_image")
    @mock.patch.object(credentials.UserController,
                   "authorize")
    def test_pull(self, mu, md):
        im_id = 'X'
        mu.return_value = True
        md.return_value = im_id
        parameters = {"token":"tokennnnnn",
                      "source": 'repoooo'}
        result = self.controller.pull(parameters)
        self.assertEqual(im_id, result)

    @mock.patch.object(docker_helper.DockerController, "pull_image")
    @mock.patch.object(credentials.UserController,
                   "authorize")
    def test_pull_unauthorized(self, mu, md):
        im_id = 'X'
        mu.side_effect = exceptions.UserCredentialsException("")
        md.return_value = im_id
        parameters = {"token":"tokennnnnn",
                      "source": 'repoooo'}
        self.assertRaises(exceptions.UserCredentialsException,
                          self.controller.pull,
                          parameters)

    @mock.patch.object(docker_helper.DockerController, "list_containers")
    @mock.patch.object(credentials.UserController, "list_containers")
    def test_list(self, mu, ml):
        c1 = uuid.uuid4().hex
        c2 = uuid.uuid4().hex
        c3 = uuid.uuid4().hex
        containers = [c1, c2, c3]
        info_containers = [{"info"}, {"info"}]
        mu.return_value = containers
        ml.return_value = info_containers
        parameters = {"token": uuid.uuid4().hex}
        results = self.controller.list_containers(parameters)
        self.assertEqual(results.__len__(), info_containers.__len__())

    @mock.patch.object(docker_helper.DockerController, "list_containers")
    @mock.patch.object(credentials.UserController, "list_containers")
    def test_list_empty(self, mu, ml):
        mu.return_value = []
        parameters = {"token": uuid.uuid4().hex}
        results = self.controller.list_containers(parameters)
        self.assertEqual([], results)

    @mock.patch.object(docker_helper.DockerController, "list_containers")
    @mock.patch.object(credentials.UserController, "list_containers")
    def test_list_unauthorized(self, mu, ml):
        mu.side_effect = exceptions.UserCredentialsException("")
        parameters = {"token": uuid.uuid4().hex}
        self.assertRaises(exceptions.UserCredentialsException,
                          self.controller.list_containers,
                          parameters)

    @mock.patch.object(docker_helper.DockerController, "container_details")
    @mock.patch.object(credentials.UserController, "authorize_container")
    def test_show(self, mu, ml):
        c1 = uuid.uuid4().hex
        info_containers = {"info"}
        mu.return_value = c1
        ml.return_value = info_containers
        parameters = {"token": uuid.uuid4().hex,
                      "container_id": c1}
        results = self.controller.show(parameters)
        self.assertEqual(info_containers, results)

    @mock.patch.object(docker_helper.DockerController, "container_details")
    @mock.patch.object(credentials.UserController, "authorize_container")
    def test_show_unauthorized(self, mu, ml):
        c1 = uuid.uuid4().hex
        info_containers = {"info"}
        mu.side_effect = exceptions.UserCredentialsException("")
        ml.return_value = info_containers
        parameters = {"token": uuid.uuid4().hex,
                      "container_id": c1}
        self.assertRaises(exceptions.UserCredentialsException,
                          self.controller.show,
                          parameters)

    @mock.patch.object(docker_helper.DockerController, "logs_container")
    @mock.patch.object(credentials.UserController, "authorize_container")
    def test_logs(self, mu, ml):
        c1 = uuid.uuid4().hex
        info_containers = {"info"}
        mu.return_value = c1
        ml.return_value = info_containers
        parameters = {"token": uuid.uuid4().hex,
                      "container_id": c1}
        results = self.controller.logs(parameters)
        self.assertEqual(info_containers, results)

    @mock.patch.object(docker_helper.DockerController, "logs_container")
    @mock.patch.object(credentials.UserController, "authorize_container")
    def test_log_unauthorized(self, mu, ml):
        c1 = uuid.uuid4().hex
        info_containers = {"info"}
        mu.side_effect = exceptions.UserCredentialsException("")
        ml.return_value = info_containers
        parameters = {"token": uuid.uuid4().hex,
                      "container_id": c1}
        self.assertRaises(exceptions.UserCredentialsException,
                          self.controller.logs,
                          parameters)

    @mock.patch.object(docker_helper.DockerController, "delete_container")
    @mock.patch.object(credentials.UserController,
                       "authorize_container")
    @mock.patch.object(credentials.UserController,
                       "remove_container")
    def test_delete(self, mr, mu, md):
        c1 = uuid.uuid4().hex
        mu.side_effect = [c1]
        parameters = {"token": uuid.uuid4().hex,
                      "container_id": c1}
        results = self.controller.delete_container(parameters)
        self.assertEqual([c1], results)

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
        parameters = {"token": uuid.uuid4().hex,
                      "container_id": [c1,c2]}
        results = self.controller.delete_container(parameters)
        self.assertEqual([c1, c2], results)

    @mock.patch.object(docker_helper.DockerController, "delete_container")
    @mock.patch.object(credentials.UserController,
                       "authorize_container")
    @mock.patch.object(credentials.UserController,
                       "remove_container")
    def test_delete_unauthorized(self, mr, mu, md):
        c1 = uuid.uuid4().hex
        mu.side_effect = exceptions.UserCredentialsException("")
        parameters = {"token": uuid.uuid4().hex,
                      "container_id": c1}
        results = self.controller.delete_container(parameters)
        self.assertEqual(1, results.__len__())
        self.assertIn("Exception", results[0])

    @mock.patch.object(docker_helper.DockerController, "delete_container")
    @mock.patch.object(credentials.UserController,
                       "authorize_container")
    @mock.patch.object(credentials.UserController,
                       "remove_container")
    def test_delete_several_unauthorized(self, mr, mu, md):
        c1 = uuid.uuid4().hex
        c2 = uuid.uuid4().hex
        c3 = uuid.uuid4().hex
        mu.side_effect = [exceptions.UserCredentialsException(""),
                          c2,
                          c3]
        parameters = {"token": uuid.uuid4().hex,
                      "container_id": [c1, c2, c3]}
        results = self.controller.delete_container(parameters)
        self.assertEqual(3, results.__len__())
        self.assertIn("Exception", results[0])
        self.assertEqual(c2, results[1])
        self.assertEqual(c3, results[2])


    @mock.patch.object(docker_helper.DockerController, "run_container")
    @mock.patch.object(credentials.UserController,
                   "authorize_directory")
    @mock.patch.object(credentials.UserController,
                       "add_container")
    @mock.patch.object(docker_helper.DockerController,
                       "start_container")
    @mock.patch.object(docker_helper.DockerController,
                       "logs_container")
    @mock.patch.object(credentials.UserController,
                       "get_job_from_token")
    def test_run_full(self, m_get_j, m_log, m_start, madd, math, mr):
        token = uuid.uuid4().hex
        image_id = uuid.uuid4().hex
        container_id = uuid.uuid4().hex
        log_info = "logsssss"
        script = 'ls'
        detach = False
        host_dir = "/foo"
        docker_dir = "/foo"
        working_dir = "/foo"
        cgroup = uuid.uuid4().hex
        madd.return_value = True
        math.return_value = True
        m_log.return_value = log_info
        m_get_j.return_value = {"cgroup": cgroup}
        mr.return_value = container_id
        parameters = {"token": token,
                      "image_id": image_id,
                      "script": script,
                      "detach": detach,
                      "host_dir": host_dir,
                      "docker_dir": docker_dir,
                      "working_dir": working_dir
                      }
        results = self.controller.run(parameters)
        self.assertEqual(log_info, results)
        math.assert_called_with(
            token,
            host_dir,
        )
        mr.assert_called_with(
            image_id,
            detach,
            script,
            host_dir=host_dir,
            docker_dir=docker_dir,
            working_dir=working_dir,
            cgroup=cgroup
        )
        madd.assert_called_with(
            token,
            container_id,
        )
        m_start.assert_called_with(
            container_id,
        )

    @mock.patch.object(docker_helper.DockerController, "run_container")
    @mock.patch.object(credentials.UserController,
                   "authorize_directory")
    @mock.patch.object(credentials.UserController,
                       "add_container")
    @mock.patch.object(docker_helper.DockerController,
                       "start_container")
    @mock.patch.object(docker_helper.DockerController,
                       "logs_container")
    @mock.patch.object(credentials.UserController,
                       "get_job_from_token")
    def test_run_No_host_dir(self, m_get_j, m_log, m_start, madd, math, mr):
        token = uuid.uuid4().hex
        image_id = uuid.uuid4().hex
        container_id = uuid.uuid4().hex
        log_info = "logsssss"
        script = 'ls'
        detach = False
        host_dir = None
        docker_dir = "/foo"
        working_dir = "/foo"
        cgroup = uuid.uuid4().hex
        madd.return_value = True
        math.return_value = True
        m_log.return_value = log_info
        m_get_j.return_value = {"cgroup": cgroup}
        mr.return_value = container_id
        parameters = {"token": token,
                      "image_id": image_id,
                      "script": script,
                      "detach": detach,
                      "host_dir": host_dir,
                      "docker_dir": docker_dir,
                      "working_dir": working_dir
                      }
        results = self.controller.run(parameters)
        self.assertEqual(log_info, results)
        self.assertIs(False, math.called)

    @mock.patch.object(docker_helper.DockerController, "run_container")
    @mock.patch.object(credentials.UserController,
                   "authorize_directory")
    @mock.patch.object(credentials.UserController,
                       "add_container")
    @mock.patch.object(docker_helper.DockerController,
                       "start_container")
    @mock.patch.object(docker_helper.DockerController,
                       "logs_container")
    @mock.patch.object(credentials.UserController,
                       "get_job_from_token")
    def test_run_detach(self, m_get_j, m_log, m_start, madd, math, mr):
        token = uuid.uuid4().hex
        image_id = uuid.uuid4().hex
        container_id = uuid.uuid4().hex
        log_info = "logsssss"
        script = 'ls'
        detach = True
        host_dir = None
        docker_dir = "/foo"
        working_dir = "/foo"
        cgroup = uuid.uuid4().hex
        madd.return_value = True
        math.return_value = True
        m_log.return_value = log_info
        m_get_j.return_value = {"cgroup": cgroup}
        mr.return_value = container_id
        parameters = {"token": token,
                      "image_id": image_id,
                      "script": script,
                      "detach": detach,
                      "host_dir": host_dir,
                      "docker_dir": docker_dir,
                      "working_dir": working_dir
                      }
        results = self.controller.run(parameters)
        self.assertEqual(container_id, results)

    @mock.patch.object(docker_helper.DockerController, "run_container")
    @mock.patch.object(credentials.UserController,
                   "authorize_directory")
    @mock.patch.object(credentials.UserController,
                       "add_container")
    @mock.patch.object(docker_helper.DockerController,
                       "start_container")
    @mock.patch.object(docker_helper.DockerController,
                       "logs_container")
    @mock.patch.object(credentials.UserController,
                       "get_job_from_token")
    def test_run_unautorized(self, m_get_j, m_log, m_start, madd, math, mr):
        token = uuid.uuid4().hex
        image_id = uuid.uuid4().hex
        container_id = uuid.uuid4().hex
        log_info = "logsssss"
        script = 'ls'
        detach = True
        host_dir = "/foo"
        docker_dir = "/foo"
        working_dir = "/foo"
        cgroup = uuid.uuid4().hex
        madd.return_value = True
        math.side_effect = exceptions.UserCredentialsException("")
        m_log.return_value = log_info
        m_get_j.return_value = {"cgroup": cgroup}
        mr.return_value = container_id
        parameters = {"token": token,
                      "image_id": image_id,
                      "script": script,
                      "detach": detach,
                      "host_dir": host_dir,
                      "docker_dir": docker_dir,
                      "working_dir": working_dir
                      }
        self.assertRaises(exceptions.UserCredentialsException,
                          self.controller.run,
                          parameters)

    @mock.patch.object(credentials.UserController, "get_job_from_token")
    @mock.patch.object(credentials.UserController, "authorize_admin")
    @mock.patch.object(batch.SGEController, "get_accounting")
    @mock.patch.object(credentials.UserController, "update_job")
    @mock.patch.object(batch.SGEController, "notify_accounting")
    def test_notify_accounting(self, m_not, m_up, m_acc, mad, mjob):
        c1 = uuid.uuid4().hex
        parameters = {"token": uuid.uuid4().hex,
                      'admin_token': uuid.uuid4().hex}
        results = self.controller.notify_accounting(parameters)

    @mock.patch.object(docker_helper.DockerController, "accounting_container")
    @mock.patch.object(credentials.UserController, "authorize_container")
    @mock.patch.object(batch.SGEController, "notify_accounting")
    def test_notify_accounting_unauthorized(self, mac, mu, ml):
        mu.side_effect = exceptions.UserCredentialsException("")
        parameters = {"token": uuid.uuid4().hex,
                      'admin_token': uuid.uuid4().hex}
        self.assertRaises(exceptions.UserCredentialsException,
                          self.controller.notify_accounting,
                          parameters)

    @mock.patch.object(docker_helper.DockerController, "stop_container")
    @mock.patch.object(credentials.UserController, "authorize_container")
    def test_stop(self, mu, ml):
        c1 = uuid.uuid4().hex
        info_containers = {"info"}
        mu.return_value = c1
        ml.return_value = info_containers
        parameters = {"token": uuid.uuid4().hex,
                      "container_id": c1}
        results = self.controller.stop_container(parameters)
        self.assertEqual(info_containers, results)

    @mock.patch.object(docker_helper.DockerController, "stop_container")
    @mock.patch.object(credentials.UserController, "authorize_container")
    def test_stop_unauthorized(self, mu, ml):
        c1 = uuid.uuid4().hex
        info_containers = {"info"}
        mu.side_effect = exceptions.UserCredentialsException("")
        ml.return_value = info_containers
        parameters = {"token": uuid.uuid4().hex,
                      "container_id": c1}
        self.assertRaises(exceptions.UserCredentialsException,
                          self.controller.stop_container,
                          parameters)

    @mock.patch.object(docker_helper.DockerController, "accounting_container")
    @mock.patch.object(credentials.UserController, "authorize_container")
    def test_accounting(self, mu, ml):
        c1 = uuid.uuid4().hex
        info_containers = {"info"}
        mu.return_value = c1
        ml.return_value = info_containers
        parameters = {"token": uuid.uuid4().hex}
        results = self.controller.accounting(parameters)
        self.assertEqual(info_containers, results)

    @mock.patch.object(docker_helper.DockerController, "accounting_container")
    @mock.patch.object(credentials.UserController, "authorize_container")
    def test_accounting_unauthorized(self, mu, ml):
        mu.side_effect = exceptions.UserCredentialsException("")
        parameters = {"token": uuid.uuid4().hex}
        self.assertRaises(exceptions.UserCredentialsException,
                          self.controller.accounting,
                          parameters)

    @mock.patch.object(docker_helper.DockerController, "output_task")
    @mock.patch.object(credentials.UserController, "authorize_container")
    def test_output(self, mu, ml):
        c1 = uuid.uuid4().hex
        info_containers = {"info"}
        mu.return_value = c1
        ml.return_value = info_containers
        parameters = {"token": uuid.uuid4().hex,
                      "container_id": c1}
        results = self.controller.output(parameters)
        self.assertEqual(info_containers, results)

    @mock.patch.object(docker_helper.DockerController, "output_task")
    @mock.patch.object(credentials.UserController, "authorize_container")
    def test_output_unauthorized(self, mu, ml):
        c1 = uuid.uuid4().hex
        info_containers = {"info"}
        mu.side_effect = exceptions.UserCredentialsException("")
        ml.return_value = info_containers
        parameters = {"token": uuid.uuid4().hex,
                      "container_id": c1}
        self.assertRaises(exceptions.UserCredentialsException,
                          self.controller.output,
                          parameters)
