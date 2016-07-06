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

from click import testing
import mock
import testtools

from bdocker.client import cli
from bdocker.modules import request


class TestCaseCommandLine(testtools.TestCase):
    runner = None

    def setUp(self):
        super(TestCaseCommandLine, self).setUp()
        self.runner = testing.CliRunner()

    def test_openstack(self):
        result = self.runner.invoke(cli.bdocker)
        self.assertEqual(0, result.exit_code)
        self.assertIsNone(result.exception)


class TestFunctionalClient(TestCaseCommandLine):

    def setUp(self):
        super(TestFunctionalClient, self).setUp()

    @mock.patch("bdocker.utils.read_file")
    @mock.patch("bdocker.utils.load_configuration_from_file")
    @mock.patch("bdocker.modules.load_batch_module")
    @mock.patch.object(request.RequestController, "execute_put")
    def test_docker_copy(self, m_put, m_batch, m_load, m_read):
        m_put.return_value = {}
        token_id = uuid.uuid4().hex
        token = "--token=%s" % token_id
        container_id = uuid.uuid4().hex
        path = "/foo"
        path_container = "%s:%s" % (container_id, path)
        path_host = "/baa"
        result = self.runner.invoke(
            cli.bdocker, ['cp', token, path_host, path_container]
        )
        self.assertEqual(0, result.exit_code)
        self.assertIsNone(result.exception)
        expected = {"token": token_id,
                    "container_id": container_id,
                    "container_path": path,
                    "host_path": path_host,
                    "host_to_container": True
                    }
        m_put.assert_called_with(path="/copy",
                                 parameters=expected)

    @mock.patch("os.remove")
    @mock.patch("bdocker.utils.read_file")
    @mock.patch("bdocker.utils.read_yaml_file")
    @mock.patch("bdocker.utils.load_configuration_from_file")
    @mock.patch("bdocker.modules.load_batch_module")
    @mock.patch.object(request.RequestController, "execute_delete")
    def test_clean(self, m_del, m_batch, m_load, m_yaml, m_read, m_delete):
        result = self.runner.invoke(
            cli.bdocker, ['clean']
        )
        self.assertEqual(result.exit_code, 0)
        self.assertIsNone(result.exception)
        self.assertEqual(True, m_delete.called)
        self.assertEqual(True, m_read.called)
        self.assertEqual(True, m_load.called)
        self.assertEqual(True, m_batch.called)
        self.assertEqual(True, m_del.called)

    @mock.patch("os.chown")
    @mock.patch("__builtin__.open")
    @mock.patch("bdocker.client.commands.get_user_credentials")
    @mock.patch("bdocker.utils.read_yaml_file")
    @mock.patch("bdocker.utils.load_configuration_from_file")
    @mock.patch("bdocker.modules.load_batch_module")
    @mock.patch.object(request.RequestController, "execute_post")
    def test_configure(self, m_post, m_batch, m_load, m_yaml,
                       m_cre, m_open, m_chown):
        result = self.runner.invoke(
            cli.bdocker, ['configure']
        )
        self.assertEqual(result.exit_code, 0)
        self.assertIsNone(result.exception)
        self.assertEqual(True, m_cre.called)
        self.assertEqual(True, m_load.called)
        self.assertEqual(True, m_yaml.called)
        self.assertEqual(True, m_chown.called)
        self.assertEqual(True, m_open.called)
        self.assertEqual(True, m_post.called)

    @mock.patch("bdocker.utils.load_configuration_from_file")
    @mock.patch("bdocker.modules.load_batch_module")
    @mock.patch.object(request.RequestController, "execute_get")
    def test_docker_list(self, m_get, m_batch, m_load):
        m_get.return_value = {}
        token = "--token=%s" % uuid.uuid4().hex
        result = self.runner.invoke(
            cli.bdocker, ['ps', token]
        )
        self.assertEqual(0, result.exit_code)
        self.assertIsNone(result.exception)

    @mock.patch("bdocker.utils.load_configuration_from_file")
    @mock.patch("bdocker.modules.load_batch_module")
    @mock.patch.object(request.RequestController, "execute_get")
    def test_docker_list_all(self, m_get, m_batch, m_load):
        m_get.return_value = {}
        all_containers = "--all"
        result = self.runner.invoke(
            cli.bdocker, ['ps', all_containers]
        )
        self.assertEqual(0, result.exit_code)
        self.assertIsNone(result.exception)

    @mock.patch("bdocker.utils.load_configuration_from_file")
    @mock.patch("bdocker.modules.load_batch_module")
    @mock.patch.object(request.RequestController, "execute_get")
    def test_docker_inspect(self, m_get, m_batch, m_load):
        m_get.return_value = {}
        token = "--token=%s" % uuid.uuid4().hex
        container_id = uuid.uuid4().hex
        result = self.runner.invoke(
            cli.bdocker, ['inspect', token, container_id]
        )
        self.assertEqual(0, result.exit_code)
        self.assertIsNone(result.exception)

    @mock.patch("bdocker.utils.load_configuration_from_file")
    @mock.patch("bdocker.modules.load_batch_module")
    @mock.patch.object(request.RequestController, "execute_get")
    def test_docker_inspect_no_container(self, m_get, m_batch, m_load):
        m_get.return_value = {}
        result = self.runner.invoke(
            cli.bdocker, ['inspect']
        )
        self.assertEqual(2, result.exit_code)
        self.assertIsNotNone(result.exception)

    @mock.patch("bdocker.utils.load_configuration_from_file")
    @mock.patch("bdocker.modules.load_batch_module")
    @mock.patch.object(request.RequestController, "execute_get")
    def test_docker_logs(self, m_get, m_batch, m_load):
        m_get.return_value = {}
        token = "--token=%s" % uuid.uuid4().hex
        container_id = uuid.uuid4().hex
        result = self.runner.invoke(
            cli.bdocker, ['logs', token, container_id]
        )
        self.assertEqual(0, result.exit_code)
        self.assertIsNone(result.exception)

    @mock.patch("bdocker.utils.load_configuration_from_file")
    @mock.patch("bdocker.modules.load_batch_module")
    @mock.patch.object(request.RequestController, "execute_get")
    def test_docker_logs_no_container(self, m_get, m_batch, m_load):
        m_get.return_value = {}
        result = self.runner.invoke(
            cli.bdocker, ['logs']
        )
        self.assertEqual(2, result.exit_code)
        self.assertIsNotNone(result.exception)

    @mock.patch("bdocker.utils.load_configuration_from_file")
    @mock.patch("bdocker.modules.load_batch_module")
    @mock.patch.object(request.RequestController, "execute_put")
    def test_docker_delete(self, m_get, m_batch, m_load):
        m_get.return_value = {}
        token = "--token=%s" % uuid.uuid4().hex
        container_id = uuid.uuid4().hex
        result = self.runner.invoke(
            cli.bdocker, ['rm', token, container_id]
        )
        self.assertEqual(0, result.exit_code)
        self.assertIsNone(result.exception)

    @mock.patch("bdocker.utils.load_configuration_from_file")
    @mock.patch("bdocker.modules.load_batch_module")
    @mock.patch.object(request.RequestController, "execute_put")
    def test_docker_delete_no_container(self, m_get, m_batch, m_load):
        m_get.return_value = {}
        result = self.runner.invoke(
            cli.bdocker, ['rm']
        )
        self.assertEqual(2, result.exit_code)
        self.assertIsNotNone(result.exception)

    @mock.patch("bdocker.utils.load_configuration_from_file")
    @mock.patch("bdocker.modules.load_batch_module")
    @mock.patch.object(request.RequestController, "execute_put")
    def test_docker_delete_several(self, m_get, m_batch, m_load):
        m_get.return_value = {}
        token = "--token=%s" % uuid.uuid4().hex
        container_id = uuid.uuid4().hex
        container_id2 = uuid.uuid4().hex
        result = self.runner.invoke(
            cli.bdocker, ['rm', token, container_id, container_id2]
        )
        self.assertEqual(result.exit_code, 0)
        self.assertIsNone(result.exception)

    @mock.patch("bdocker.utils.load_configuration_from_file")
    @mock.patch("bdocker.modules.load_batch_module")
    @mock.patch.object(request.RequestController, "execute_put")
    def test_docker_run(self, m_rq, m_batch, m_load):
        m_rq.return_value = {}
        token_id = uuid.uuid4().hex
        token = "--token=%s" % token_id
        image_id = uuid.uuid4().hex
        command = 'ls'
        result = self.runner.invoke(
            cli.bdocker, ['run', token, image_id, command]
        )
        self.assertEqual(result.exit_code, 0)
        self.assertIsNone(result.exception)
        expected = {
            "token": token_id,
            "image_id": image_id,
            "script": command,
            "detach": None
        }
        m_rq.assert_called_with(path="/run", parameters=expected)

    @mock.patch("bdocker.utils.load_configuration_from_file")
    @mock.patch("bdocker.modules.load_batch_module")
    @mock.patch.object(request.RequestController, "execute_put")
    def test_docker_run_volume(self, m_rq, m_batch, m_load):
        m_rq.return_value = {}
        token_id = uuid.uuid4().hex
        token = "--token=%s" % token_id
        image_id = uuid.uuid4().hex
        command = 'ls'
        host_path = "/foo"
        doc_path = "/baa"
        w_path = "/work"
        work_dir = "--workdir=%s" % w_path
        volume = '--volume=%s:%s' % (host_path, doc_path)
        result = self.runner.invoke(
            cli.bdocker, ['run', token,
                          image_id, work_dir,
                          command, volume]
        )
        self.assertEqual(result.exit_code, 0)
        self.assertIsNone(result.exception)
        expected = {"host_dir": host_path,
                    "docker_dir": doc_path,
                    "token": token_id,
                    "image_id": image_id,
                    "script": command,
                    "working_dir": w_path,
                    "detach": None
                    }
        m_rq.assert_called_with(path="/run",
                                parameters=expected)
