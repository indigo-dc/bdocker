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
from click.testing import CliRunner

from bdocker.client import cli
from bdocker.modules import request


class TestCaseCommandLine(testtools.TestCase):
    runner = None

    def setUp(self):
        super(TestCaseCommandLine, self).setUp()
        self.runner = CliRunner()

    def test_openstack(self):
        result = self.runner.invoke(cli.bdocker)
        self.assertEqual(result.exit_code,0)
        self.assertIsNone(result.exception)


class TestCommandProject(TestCaseCommandLine):

    def setUp(self):
        super(TestCommandProject, self).setUp()

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
        self.assertEqual(result.exit_code,0)
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
    def test_batch_clean(self, m_del, m_batch, m_load, m_yaml, m_read, m_delete):
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
    def test_batch_configure(self, m_post, m_batch, m_load, m_yaml,
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
        self.assertEqual(result.exit_code,0)
        self.assertIsNone(result.exception)