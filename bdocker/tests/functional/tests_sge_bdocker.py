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
import os
import uuid

import docker as docker_py
import mock
import testtools
import webob
from cgroupspy import nodes
from click import testing

import bdocker.tests.fakes as fakes
from bdocker.api import working_node
from bdocker.client import cli
from bdocker.modules import batch


class TestBdockerSgeWn(testtools.TestCase):
    """Tests the all workflow of Bdocker commands."""

    def setUp(self):
        super(TestBdockerSgeWn, self).setUp()
        self.file_name = os.path.join(os.path.dirname(__file__),
                                      'sge_wn_configure.cfg')
        self.token_store = copy.deepcopy(fakes.token_store)
        self.admin_token = self.token_store["prolog"]["token"]
        self.app = working_node.app
        self.runner = testing.CliRunner()

    @mock.patch("os.getenv")
    @mock.patch.object(docker_py.Client, "containers")
    @mock.patch.object(batch.SGEController, "get_job_info")
    def test_docker_list(self, m_inf, m_list, m_env):
        token = fakes.user_token
        containers = self.token_store[token]["containers"]
        m_env.return_value = self.file_name
        m_list.return_value = [
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
        orig = webob.Request.get_response
        app = self.app

        def mocked_some_method(self, bar=None):
            if bar:
                return orig(self, bar)
            else:
                return orig(self, app)

        token = "--token=%s" % token
        with mock.patch("bdocker.utils.read_yaml_file",
                        return_value=fakes.token_store
                        ):
            with mock.patch("os.getenv",
                            return_value=self.file_name
                            ):
                with mock.patch("webob.Request.get_response",
                                side_effect=mocked_some_method,
                                autospec=True) as mock_method:
                    result = self.runner.invoke(
                        cli.bdocker, ['ps', token]
                    )
                    assert mock_method.called
        self.assertEqual(result.exit_code, 0)
        self.assertIsNone(result.exception)
        self.assertIn(containers[0][:12], result.output)
        self.assertIn(containers[1][:12], result.output)

    @mock.patch("os.getenv")
    @mock.patch.object(docker_py.Client, "inspect_container")
    @mock.patch.object(batch.SGEController, "get_job_info")
    def test_docker_inspect(self, m_inf, m_ins, m_env):
        m_env.return_value = self.file_name
        token = fakes.user_token
        containers = self.token_store[token]["containers"]
        container_id = containers[0]
        m_ins.return_value = {
            "containerId": container_id,
            "command": "ls"
        }
        orig = webob.Request.get_response
        app = self.app

        def mocked_some_method(self, bar=None):
            if bar:
                return orig(self, bar)
            else:
                return orig(self, app)

        token = "--token=%s" % token
        with mock.patch("bdocker.utils.read_yaml_file",
                        return_value=fakes.token_store
                        ):
            with mock.patch("os.getenv",
                            return_value=self.file_name
                            ):
                with mock.patch("webob.Request.get_response",
                                side_effect=mocked_some_method,
                                autospec=True) as mock_method:
                    result = self.runner.invoke(
                        cli.bdocker, ['inspect', token, container_id]
                    )
                    assert mock_method.called

        self.assertEqual(0, result.exit_code)
        self.assertIsNone(result.exception)
        self.assertIn(container_id, result.output)

    @mock.patch("os.getenv")
    @mock.patch.object(docker_py.Client, "logs")
    @mock.patch.object(batch.SGEController, "get_job_info")
    def test_docker_logs(self, m_get, m_logs, m_env):
        m_env.return_value = self.file_name
        token = fakes.user_token
        container_id = self.token_store[token]["containers"][0]
        logs = [uuid.uuid4().hex, uuid.uuid4().hex]

        def create_log():
            for l in logs:
                yield(l)
        m_logs.return_value = create_log()
        orig = webob.Request.get_response
        app = self.app

        def mocked_some_method(self, bar=None):
            if bar:
                return orig(self, bar)
            else:
                return orig(self, app)
        token = "--token=%s" % token
        with mock.patch("bdocker.utils.read_yaml_file",
                        return_value=fakes.token_store
                        ):
            with mock.patch("os.getenv",
                            return_value=self.file_name
                            ):
                with mock.patch("webob.Request.get_response",
                                side_effect=mocked_some_method,
                                autospec=True) as mock_method:
                    result = self.runner.invoke(
                        cli.bdocker, ['logs', token, container_id]
                    )
            assert mock_method.called

        self.assertEqual(0, result.exit_code)
        self.assertIsNone(result.exception)
        self.assertEqual("\n".join(logs) + "\n", result.output)

    @mock.patch("os.getenv")
    @mock.patch.object(docker_py.Client, "remove_container")
    @mock.patch.object(batch.SGEController, "get_job_info")
    @mock.patch("bdocker.utils.write_yaml_file")
    @mock.patch("bdocker.utils.read_yaml_file")
    def test_docker_delete(self, m_r, m_w, m_inf, m_rm, m_env):
        m_env.return_value = self.file_name
        token = fakes.user_token_delete
        containers = copy.copy(
            self.token_store[token]["containers"]
        )
        m_r.return_value = self.token_store
        token_param = "--token=%s" % token

        orig = webob.Request.get_response
        app = self.app

        def mocked_some_method(self, bar=None):
            if bar:
                return orig(self, bar)
            else:
                return orig(self, app)
        with mock.patch("os.getenv",
                        return_value=self.file_name
                        ):
            with mock.patch("webob.Request.get_response",
                            side_effect=mocked_some_method,
                            autospec=True) as mock_method:
                result = self.runner.invoke(
                    cli.bdocker, ['rm', token_param,
                                  containers[0],
                                  containers[1]]
                )
                assert mock_method.called
        self.assertEqual(0, result.exit_code)
        self.assertIsNone(result.exception)
        self.assertIn(containers[0], result.output)
        self.assertIn(containers[1], result.output)
        self.assertNotIn("containers",
                         self.token_store[token])

    @mock.patch("os.getenv")
    @mock.patch.object(batch.SGEController, "get_job_info")
    @mock.patch.object(docker_py.Client, "create_container")
    @mock.patch.object(docker_py.Client, "start")
    @mock.patch.object(docker_py.Client, "logs")
    @mock.patch("bdocker.utils.write_yaml_file")
    @mock.patch("bdocker.utils.read_yaml_file")
    def test_docker_run_detach(self, m_r, m_w, m_log,
                               m_start, m_cre, m_inf, m_env):
        m_env.return_value = self.file_name
        token = fakes.user_token
        user_home = self.token_store[token]["home"]
        m_r.return_value = self.token_store
        container_id = uuid.uuid4().hex
        m_cre.return_value = {'Id': container_id}
        token_param = "--token=%s" % token
        image_id = uuid.uuid4().hex
        command = 'ls'
        host_path = user_home
        doc_path = "/baa"
        w_path = "/work"
        work_dir = "--workdir=%s" % w_path
        detach = "--detach"
        volume = '--volume=%s:%s' % (host_path, doc_path)
        orig = webob.Request.get_response
        app = self.app

        def mocked_some_method(self, bar=None):
            if bar:
                return orig(self, bar)
            else:
                return orig(self, app)
        with mock.patch("os.getenv",
                        return_value=self.file_name
                        ):
            with mock.patch("webob.Request.get_response",
                            side_effect=mocked_some_method,
                            autospec=True) as mock_method:
                result = self.runner.invoke(
                    cli.bdocker, ['run', token_param, detach,
                                  image_id, work_dir,
                                  command, volume]
                )
                assert mock_method.called
        self.assertEqual(0, result.exit_code)
        self.assertIsNone(result.exception)
        self.assertEqual("%s\n" % container_id, result.output)

    @mock.patch("os.getenv")
    @mock.patch.object(batch.SGEController, "get_job_info")
    @mock.patch.object(docker_py.Client, "create_container")
    @mock.patch.object(docker_py.Client, "start")
    @mock.patch.object(docker_py.Client, "logs")
    @mock.patch("bdocker.utils.write_yaml_file")
    @mock.patch("bdocker.utils.read_yaml_file")
    def test_docker_run_logs(self, m_r, m_w, m_log,
                             m_start, m_cre, m_inf, m_env):
        m_env.return_value = self.file_name
        token = fakes.user_token
        user_home = self.token_store[token]["home"]
        m_r.return_value = self.token_store
        container_id = uuid.uuid4().hex
        m_cre.return_value = {'Id': container_id}
        logs = [uuid.uuid4().hex, uuid.uuid4().hex]

        def create_log():
            for l in logs:
                yield(l)
        m_log.return_value = create_log()

        token = "--token=%s" % token
        image_id = uuid.uuid4().hex
        command = 'ls'
        host_path = user_home
        doc_path = "/baa"
        w_path = "/work"
        work_dir = "--workdir=%s" % w_path
        volume = '--volume=%s:%s' % (host_path, doc_path)
        orig = webob.Request.get_response
        app = self.app

        def mocked_some_method(self, bar=None):
            if bar:
                return orig(self, bar)
            else:
                return orig(self, app)
        with mock.patch("os.getenv",
                        return_value=self.file_name
                        ):
            with mock.patch("webob.Request.get_response",
                            side_effect=mocked_some_method,
                            autospec=True) as mock_method:
                result = self.runner.invoke(
                    cli.bdocker, ['run', token,
                                  image_id, work_dir,
                                  command, volume]
                )
                assert mock_method.called
        self.assertEqual(0, result.exit_code)
        self.assertIsNone(result.exception)
        self.assertEqual("\n".join(logs) + "\n", result.output)

    @mock.patch("os.getenv")
    @mock.patch.object(batch.SGEController, "get_job_info")
    @mock.patch.object(docker_py.Client, "put_archive")
    @mock.patch("bdocker.utils.read_tar_raw_data_stream")
    @mock.patch("bdocker.utils.read_file")
    def test_cp_to_container(self, m_re, m_str,
                             m_put, m_inf, m_env):
        m_env.return_value = self.file_name
        token = fakes.user_token
        containers_id = self.token_store[token]["containers"][0]
        path_host = self.token_store[token]["home"]
        m_put.return_value = True
        token_param = "--token=%s" % token
        path = "/foo"
        path_container = "%s:%s" % (containers_id, path)

        orig = webob.Request.get_response
        app = self.app

        def mocked_some_method(self, bar=None):
            if bar:
                return orig(self, bar)
            else:
                return orig(self, app)
        with mock.patch("bdocker.utils.read_yaml_file",
                        return_value=fakes.token_store
                        ):
            with mock.patch("os.getenv",
                            return_value=self.file_name
                            ):
                with mock.patch("webob.Request.get_response",
                                side_effect=mocked_some_method,
                                autospec=True) as mock_method:
                    result = self.runner.invoke(
                        cli.bdocker, ['cp', token_param,
                                      path_host, path_container]
                    )
                    assert mock_method.called
        self.assertEqual(0, result.exit_code)
        self.assertIsNone(result.exception)
        self.assertEqual("%s\n" % True, result.output)

    @mock.patch("os.getenv")
    @mock.patch.object(batch.SGEController, "get_job_info")
    @mock.patch.object(docker_py.Client, "get_archive")
    @mock.patch("bdocker.utils.write_tar_raw_data_stream")
    @mock.patch("bdocker.utils.read_file")
    def test_cp_from_container(self, m_re, m_str,
                               m_get, m_inf, m_env):
        m_env.return_value = self.file_name
        out = mock.MagicMock()
        out.data = None
        stat = {'linkTarget': '',
                'mode': 493,
                'mtime': '2015-09-16T12:34:23-07:00',
                'name': 'sh',
                'size': 962860
                }
        m_get.return_value = out, stat
        token = fakes.user_token
        containers_id = self.token_store[token]["containers"][0]
        path_host = self.token_store[token]["home"]
        token_param = "--token=%s" % token
        path = "/foo"
        path_container = "%s:%s" % (containers_id, path)

        orig = webob.Request.get_response
        app = self.app

        def mocked_some_method(self, bar=None):
            if bar:
                return orig(self, bar)
            else:
                return orig(self, app)
        with mock.patch("bdocker.utils.read_yaml_file",
                        return_value=fakes.token_store
                        ):
            with mock.patch("os.getenv",
                            return_value=self.file_name
                            ):
                with mock.patch("webob.Request.get_response",
                                side_effect=mocked_some_method,
                                autospec=True) as mock_method:
                    result = self.runner.invoke(
                        cli.bdocker, ['cp', token_param, path_container,
                                      path_host]
                    )
                    assert mock_method.called
        self.assertEqual(0, result.exit_code)
        self.assertIsNone(result.exception)
        expected = []
        for k, v in stat.items():
            expected.append("%s: %s" % (k, v))
        self.assertEqual("\n".join(expected) + "\n",
                         result.output)

    @mock.patch("pwd.getpwuid")
    @mock.patch("os.path.realpath")
    @mock.patch("bdocker.utils.write_yaml_file")
    @mock.patch("bdocker.utils.read_yaml_file")
    @mock.patch("bdocker.utils.read_file")
    @mock.patch.object(nodes.Node, "create_cgroup")
    @mock.patch.object(uuid, "uuid4")
    @mock.patch("os.fork")
    @mock.patch("bdocker.utils.update_yaml_file")
    @mock.patch("os.setsid")
    @mock.patch("os.kill")
    @mock.patch("time.sleep")
    @mock.patch("os.chown")
    @mock.patch("pwd.getpwnam")
    @mock.patch("os.getenv")
    @mock.patch.object(batch.SGEController, "_get_job_configuration")
    @mock.patch("bdocker.client.commands.write_user_credentials")
    def test_configure(self, m_wfile,
                       m_jinfo, m_env,
                       m_get_cre, m_chown,
                       m_time, m_kill,
                       m_setsid, m_up, m_fork,
                       m_uuid, m_cre, m_r, m_ry, m_w,
                       m_path, m_getpi):
        """Test configuration command.

        :param m_wfile:
        :param m_jinfo:
        :param m_env:
        :param m_get_cre:
        :param m_chown:
        :param m_time:
        :param m_kill:
        :param m_setsid:
        :param m_up:
        :param m_fork:
        :param m_uuid:
        :param m_cre:
        :param m_r:
        :param m_ry:
        :param m_w:
        :param m_path:
        :param m_getpi:
        :return:
        """
        token = uuid.uuid4().hex
        user_home = "/ttt"
        user_name = "federico"
        spool = "/rr"
        job_id = fakes.job_id
        user_uid = 33
        user_gid = 33
        m_env.side_effect = [self.file_name,
                             job_id,
                             user_home,
                             user_name,
                             spool]
        m_jinfo.return_value = fakes.job_info
        mock_pwd = mock.MagicMock()
        mock_pwd.pw_uid = user_uid
        mock_pwd.pw_gid = user_gid
        m_get_cre.return_value = mock_pwd
        cpu_usage = 5
        memory_usage = 1
        job_pid = 33

        m_r.side_effect = [None, memory_usage,
                           cpu_usage, job_pid]
        m_fork.return_value = 0
        m_ry.return_value = self.token_store
        mock_uid = mock.MagicMock()
        mock_uid.hex = token
        m_uuid.return_value = mock_uid
        m_class = mock.MagicMock()
        m_class.pw_gid = user_gid
        m_getpi.return_value = m_class
        m_path.return_value = user_home
        orig = webob.Request.get_response
        app = self.app

        def mocked_some_method(self, bar=None):
            if bar:
                return orig(self, bar)
            else:
                return orig(self, app)
        with mock.patch("os.getenv",
                        return_value=self.file_name
                        ):
            with mock.patch("webob.Request.get_response",
                            side_effect=mocked_some_method,
                            autospec=True) as mock_method:
                result = self.runner.invoke(
                    cli.bdocker, ['configure']
                )
                assert mock_method.called

        self.assertEqual(result.exit_code, 0)
        self.assertIsNone(result.exception)
        self.assertEqual("%s/.bdocker_token_%s\n"
                         % (user_home, job_id),
                         result.output
                         )

    @mock.patch("os.getenv")
    @mock.patch.object(batch.SGEController, "get_job_info")
    @mock.patch("os.remove")
    @mock.patch.object(nodes.Node, "delete_cgroup")
    @mock.patch("bdocker.utils.read_file")
    @mock.patch("bdocker.utils.add_to_file")
    @mock.patch("bdocker.utils.delete_file")
    @mock.patch("bdocker.utils.read_yaml_file")
    @mock.patch("bdocker.utils.write_yaml_file")
    @mock.patch.object(docker_py.Client, "remove_container")
    def test_batch_clean(self, m_dock, m_w, m_ry,
                         m_del, m_add, m_r,
                         m_delgroup, m_osre,
                         m_getjob, m_env):
        m_env.return_value = self.file_name
        token = fakes.user_token_clean
        m_ry.side_effect = [self.token_store,
                            fakes.job_info,
                            self.token_store,
                            ]
        user_token = fakes.user_token
        token = "--token=%s" % user_token
        orig = webob.Request.get_response
        app = self.app

        def mocked_some_method(self, bar=None):
            if bar:
                return orig(self, bar)
            else:
                if 'clean' in self.path:
                    return orig(self, app)
                else:
                    acc_app = fakes.create_accounting_app()
                    return orig(self, acc_app)
        with mock.patch("os.getenv",
                        return_value=self.file_name
                        ):
            with mock.patch("webob.Request.get_response",
                            side_effect=mocked_some_method,
                            autospec=True) as mock_method:
                result = self.runner.invoke(
                    cli.bdocker, ['clean', token]
                )
                assert mock_method.called
        self.assertEqual(result.exit_code, 0)
        self.assertIsNone(result.exception)
