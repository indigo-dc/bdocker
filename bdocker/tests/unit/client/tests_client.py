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
from bdocker.client import commands
from bdocker.client import decorators


class TestCaseCommandLine(testtools.TestCase):
    runner = None

    def setUp(self):
        super(TestCaseCommandLine, self).setUp()
        self.runner = testing.CliRunner()

    def test_openstack(self):
        result = self.runner.invoke(cli.bdocker)
        self.assertEqual(0, result.exit_code)
        self.assertIsNone(result.exception)


class TestCommandProject(TestCaseCommandLine):

    def setUp(self):
        super(TestCommandProject, self).setUp()

    def test_parse_vol(self):
        h_dir = "/root/docker_test/"
        d_dir = "/tmp"
        volume_path = "%s:%s" % (h_dir, d_dir)
        vol = decorators.parse_volume(None, None, volume_path)
        self.assertEqual(h_dir, vol['host_dir'])
        self.assertEqual(d_dir, vol['docker_dir'])

    def test_parse_vol_empty(self):
        volume_path = None
        vol = decorators.parse_volume(None, None, volume_path)
        self.assertIsNone(vol)

    @mock.patch.object(commands.CommandController, "__init__")
    @mock.patch.object(commands.CommandController, "configuration")
    def test_configure(self, m_cre, m_ini):
        m_ini.return_value = None
        token = uuid.uuid4().hex
        path = '/path'
        m_cre.return_value = {"token": token, "path": path}
        user_name = '--user=foo'
        result = self.runner.invoke(
            cli.bdocker, ['configure', user_name]
        )
        self.assertEqual(result.exit_code, 0)
        self.assertIsNone(result.exception)

    @mock.patch.object(commands.CommandController, "__init__")
    @mock.patch.object(commands.CommandController, "container_list")
    def test_docker_list(self, m_l, m_ini):
        m_ini.return_value = None
        m_l.return_value = {}
        token = "--token=%s" % uuid.uuid4().hex
        result = self.runner.invoke(
            cli.bdocker, ['ps', token]
        )
        self.assertEqual(0, result.exit_code)
        self.assertIsNone(result.exception)

    @mock.patch.object(commands.CommandController, "__init__")
    @mock.patch.object(commands.CommandController, "container_list")
    def test_docker_list_all(self, m_l, m_ini):
        m_ini.return_value = None
        m_l.return_value = {}
        all_containers = "--all"
        result = self.runner.invoke(
            cli.bdocker, ['ps', all_containers]
        )
        self.assertEqual(0, result.exit_code)
        self.assertIsNone(result.exception)
        m_l.assert_called_with(None, True)

    @mock.patch.object(commands.CommandController, "__init__")
    @mock.patch.object(commands.CommandController, "container_pull")
    def test_docker_pull(self, m_l, m_ini):
        m_ini.return_value = None
        m_l.return_value = {}
        token = "--token=%s" % uuid.uuid4().hex
        source = uuid.uuid4().hex
        result = self.runner.invoke(
            cli.bdocker, ['pull', token, source]
        )
        self.assertEqual(result.exit_code, 0)
        self.assertIsNone(result.exception)

    @mock.patch.object(commands.CommandController, "__init__")
    @mock.patch.object(commands.CommandController, "container_pull")
    def test_docker_pull_no_token(self, m_l, m_ini):
        m_ini.return_value = None
        m_l.return_value = {}
        source = uuid.uuid4().hex
        result = self.runner.invoke(
            cli.bdocker, ['pull', source]
        )
        self.assertEqual(result.exit_code, 0)
        self.assertIsNone(result.exception)

    @mock.patch.object(commands.CommandController, "__init__")
    @mock.patch.object(commands.CommandController, "container_pull")
    def test_docker_pull_no_source(self, m_l, m_ini):
        m_ini.return_value = None
        m_l.return_value = {}
        token = "--token=%s" % uuid.uuid4().hex
        result = self.runner.invoke(
            cli.bdocker, ['pull', token]
        )
        self.assertEqual(result.exit_code, 2)
        self.assertIsNotNone(result.exception)

    @mock.patch.object(commands.CommandController, "__init__")
    @mock.patch.object(commands.CommandController, "container_logs")
    def test_docker_log(self, m_l, m_ini):
        m_ini.return_value = None
        m_l.return_value = {}
        token = "--token=%s" % uuid.uuid4().hex
        container_id = uuid.uuid4().hex
        result = self.runner.invoke(
            cli.bdocker, ['logs', token, container_id]
        )
        self.assertEqual(result.exit_code, 0)
        self.assertIsNone(result.exception)

    @mock.patch.object(commands.CommandController, "__init__")
    @mock.patch.object(commands.CommandController, "container_logs")
    def test_docker_log_no_token(self, m_l, m_ini):
        m_ini.return_value = None
        m_l.return_value = {}
        container_id = uuid.uuid4().hex
        result = self.runner.invoke(
            cli.bdocker, ['logs', container_id]
        )
        self.assertEqual(result.exit_code, 0)
        self.assertIsNone(result.exception)

    @mock.patch.object(commands.CommandController, "__init__")
    @mock.patch.object(commands.CommandController, "container_logs")
    def test_docker_log_no_id(self, m_l, m_ini):
        m_ini.return_value = None
        m_l.return_value = {}
        token = "--token=%s" % uuid.uuid4().hex
        result = self.runner.invoke(
            cli.bdocker, ['logs', token]
        )
        self.assertEqual(result.exit_code, 2)
        self.assertIsNotNone(result.exception)

    @mock.patch.object(commands.CommandController, "__init__")
    @mock.patch.object(commands.CommandController, "container_inspect")
    def test_docker_inspect(self, m_l, m_ini):
        m_ini.return_value = None
        m_l.return_value = {}
        token = "--token=%s" % uuid.uuid4().hex
        container_id = uuid.uuid4().hex
        result = self.runner.invoke(
            cli.bdocker, ['inspect', token, container_id]
        )
        self.assertEqual(0, result.exit_code)
        self.assertIsNone(result.exception)

    @mock.patch.object(commands.CommandController, "__init__")
    @mock.patch.object(commands.CommandController, "container_inspect")
    def test_docker_linspect_no_token(self, m_l, m_ini):
        m_ini.return_value = None
        m_l.return_value = {}
        contanier_id = uuid.uuid4().hex
        result = self.runner.invoke(
            cli.bdocker, ['inspect', contanier_id]
        )
        self.assertEqual(0, result.exit_code)
        self.assertIsNone(result.exception)

    @mock.patch.object(commands.CommandController, "__init__")
    @mock.patch.object(commands.CommandController, "container_inspect")
    def test_docker_inspect_no_id(self, m_l, m_ini):
        m_ini.return_value = None
        m_l.return_value = {}
        token = "--token=%s" % uuid.uuid4().hex
        result = self.runner.invoke(
            cli.bdocker, ['inspect', token]
        )
        self.assertEqual(result.exit_code, 2)
        self.assertIsNotNone(result.exception)

    @mock.patch.object(commands.CommandController, "__init__")
    @mock.patch.object(commands.CommandController, "container_delete")
    def test_docker_delete(self, m_l, m_ini):
        m_ini.return_value = None
        m_l.return_value = {}
        token = "--token=%s" % uuid.uuid4().hex
        container_id = uuid.uuid4().hex
        result = self.runner.invoke(
            cli.bdocker, ['rm', container_id, token]
        )
        self.assertEqual(0, result.exit_code)
        self.assertIsNone(result.exception)

    @mock.patch.object(commands.CommandController, "__init__")
    @mock.patch.object(commands.CommandController, "container_delete")
    def test_docker_delete_no_token(self, m_l, m_ini):
        m_ini.return_value = None
        m_l.return_value = {}
        container_id = uuid.uuid4().hex
        result = self.runner.invoke(
            cli.bdocker, ['rm', container_id]
        )
        self.assertEqual(0, result.exit_code)
        self.assertIsNone(result.exception)

    @mock.patch.object(commands.CommandController, "__init__")
    @mock.patch.object(commands.CommandController, "container_delete")
    def test_docker_delete_no_id(self, m_l, m_ini):
        m_ini.return_value = None
        m_l.return_value = {}
        token = uuid.uuid4().hex
        result = self.runner.invoke(
            cli.bdocker, ['rm', "--token=%s" % token]
        )
        self.assertEqual(result.exit_code, 2)
        self.assertIsNotNone(result.exception)

    @mock.patch.object(commands.CommandController, "__init__")
    @mock.patch.object(commands.CommandController, "container_delete")
    def test_docker_delete_list(self, m_l, m_ini):
        m_ini.return_value = None
        m_l.return_value = {}
        c1 = uuid.uuid4().hex
        c2 = uuid.uuid4().hex
        token = uuid.uuid4().hex
        result = self.runner.invoke(
            cli.bdocker, ['rm', "--token=%s" % token, c1, c2]
        )
        self.assertEqual(0, result.exit_code)
        self.assertIsNone(result.exception)

    @mock.patch.object(commands.CommandController, "__init__")
    @mock.patch.object(commands.CommandController, "container_delete")
    def test_docker_delete_force(self, m_l, m_ini):
        m_ini.return_value = None
        m_l.return_value = {}
        container_id = uuid.uuid4().hex
        force = "--force"
        result = self.runner.invoke(
            cli.bdocker, ['rm', container_id, force]
        )
        self.assertEqual(0, result.exit_code)
        self.assertIsNone(result.exception)
        m_l.assert_called_with(None, mock.ANY, True)

    @mock.patch.object(commands.CommandController, "__init__")
    @mock.patch.object(commands.CommandController, "container_run")
    def test_docker_run(self, m_l, m_ini):
        m_ini.return_value = None
        m_l.return_value = {}
        token = "--token=%s" % uuid.uuid4().hex
        image_id = uuid.uuid4().hex
        command = 'ls'
        result = self.runner.invoke(
            cli.bdocker, ['run', token, image_id, command]
        )
        self.assertEqual(0, result.exit_code)
        self.assertIsNone(result.exception)

    @mock.patch.object(commands.CommandController, "__init__")
    @mock.patch.object(commands.CommandController, "container_run")
    def test_docker_run_volume(self, m_l, m_ini):
        m_ini.return_value = None
        m_l.return_value = {}
        token = "--token=%s" % uuid.uuid4().hex
        image_id = uuid.uuid4().hex
        command = 'ls'
        host_path = "/foo"
        doc_path = "/baa"
        volume = '--volume=%s:%s' % (host_path, doc_path)
        result = self.runner.invoke(
            cli.bdocker, ['run', token,
                          image_id,
                          command, volume]
        )
        self.assertEqual(0, result.exit_code)
        self.assertIsNone(result.exception)

    @mock.patch.object(commands.CommandController, "__init__")
    @mock.patch.object(commands.CommandController, "container_run")
    def test_docker_run_detach(self, m_l, m_ini):
        m_ini.return_value = None
        m_l.return_value = {}
        token = "--token=%s" % uuid.uuid4().hex
        image_id = uuid.uuid4().hex
        command = 'ls'
        detach = '--detach'
        result = self.runner.invoke(
            cli.bdocker, ['run', token,
                          image_id,
                          command, detach]
        )
        self.assertEqual(0, result.exit_code)
        self.assertIsNone(result.exception)

    @mock.patch.object(commands.CommandController, "__init__")
    @mock.patch.object(commands.CommandController, "container_run")
    def test_docker_run_workdir(self, m_l, m_ini):
        m_ini.return_value = None
        m_l.return_value = {}
        token = "--token=%s" % uuid.uuid4().hex
        image_id = uuid.uuid4().hex
        command = 'ls'
        workdir = '--workdir=fake'
        result = self.runner.invoke(
            cli.bdocker, ['run', token, image_id,
                          command, workdir]
        )
        self.assertEqual(0, result.exit_code)
        self.assertIsNone(result.exception)

    @mock.patch.object(commands.CommandController, "__init__")
    @mock.patch.object(commands.CommandController, "container_run")
    def test_docker_run_err(self, m_l, m_ini):
        m_ini.return_value = None
        m_l.return_value = {}
        token = "--token=%s" % uuid.uuid4().hex
        image_id = uuid.uuid4().hex
        command = 'ls'
        workdir = '--workdddir=fake'
        result = self.runner.invoke(
            cli.bdocker, ['run', token, image_id,
                          command, workdir]
        )
        self.assertEqual(2, result.exit_code)
        self.assertIsNotNone(result.exception)

    @mock.patch.object(commands.CommandController, "__init__")
    @mock.patch.object(commands.CommandController, "container_run")
    def test_docker_run_host(self, m_l, m_ini):
        m_ini.return_value = None
        m_l.return_value = {}
        token = "--token=%s" % uuid.uuid4().hex
        image_id = uuid.uuid4().hex
        command = 'ls'
        host = '--host=fake:5000'
        result = self.runner.invoke(
            cli.bdocker, [host, 'run', token, image_id,
                          command]
        )
        self.assertEqual(0, result.exit_code)
        self.assertIsNone(result.exception)

    @mock.patch.object(commands.CommandController, "__init__")
    @mock.patch.object(commands.CommandController, "clean_environment")
    def test_batch_clean(self, m_cre, m_ini):
        m_ini.return_value = None
        result = self.runner.invoke(
            cli.bdocker, ['clean']
        )
        self.assertEqual(0, result.exit_code)
        self.assertIsNone(result.exception)

    @mock.patch.object(commands.CommandController, "__init__")
    @mock.patch.object(commands.CommandController, "clean_environment")
    def test_clean_with_token(self, m_cre, m_ini):
        m_ini.return_value = None
        token = uuid.uuid4().hex
        m_cre.return_value = {"token": token}
        token_var = '--token=%s' % token
        result = self.runner.invoke(
            cli.bdocker, ['clean', token_var]
        )
        self.assertEqual(0, result.exit_code)
        self.assertIsNone(result.exception)

    @mock.patch.object(commands.CommandController, "__init__")
    @mock.patch.object(commands.CommandController, "copy_to_from_container")
    def test_docker_copy(self, m_l, m_ini):
        m_ini.return_value = None
        m_l.return_value = {}
        token = "--token=%s" % uuid.uuid4().hex
        container_id = uuid.uuid4().hex
        path = "/foo"
        path2 = "%s:/foo" % container_id
        result = self.runner.invoke(
            cli.bdocker, ['cp', token, path, path2]
        )
        self.assertEqual(0, result.exit_code)
        self.assertIsNone(result.exception)

    @mock.patch.object(commands.CommandController, "__init__")
    @mock.patch.object(commands.CommandController, "copy_to_from_container")
    def test_docker_copy_to_container(self, m_l, m_ini):
        m_ini.return_value = None
        m_l.return_value = {}
        token = "--token=%s" % uuid.uuid4().hex
        container_id = uuid.uuid4().hex
        path = "%s:/foo" % container_id
        path2 = "/foo"
        result = self.runner.invoke(
            cli.bdocker, ['cp', token, path, path2]
        )
        self.assertEqual(0, result.exit_code)
        self.assertIsNone(result.exception)

    @mock.patch.object(commands.CommandController, "__init__")
    @mock.patch.object(commands.CommandController, "copy_to_from_container")
    def test_docker_copy_no_token(self, m_l, m_ini):
        m_ini.return_value = None
        m_l.return_value = {}
        container_id = uuid.uuid4().hex
        path = "/foo"
        path2 = "%s:/foo" % container_id
        result = self.runner.invoke(
            cli.bdocker, ['cp', path, path2]
        )
        self.assertEqual(0, result.exit_code)
        self.assertIsNone(result.exception)

    @mock.patch.object(commands.CommandController, "__init__")
    @mock.patch.object(commands.CommandController, "copy_to_from_container")
    def test_docker_copy_no_id(self, m_l, m_ini):
        m_ini.return_value = None
        m_l.return_value = {}
        path = "/foo"
        path2 = "/foo2"
        result = self.runner.invoke(
            cli.bdocker, ['cp', path, path2]
        )
        self.assertEqual(result.exit_code, 2)
        self.assertIsNotNone(result.exception)

    @mock.patch.object(commands.CommandController, "__init__")
    @mock.patch.object(commands.CommandController, "copy_to_from_container")
    def test_docker_copy_miss_path(self, m_l, m_ini):
        m_ini.return_value = None
        m_l.return_value = {}
        path = "/path"
        result = self.runner.invoke(
            cli.bdocker, ['cp', path]
        )
        self.assertEqual(2, result.exit_code)
        self.assertIsNotNone(result.exception)

    # TODO(jorgesece): include teste for
    # clean
    # notify_accounting
    # more....
