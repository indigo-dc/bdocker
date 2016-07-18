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

from bdocker.client import commands
from bdocker import exceptions
from bdocker.modules import request
from bdocker.tests import fakes


class TestCommands(testtools.TestCase):
    """Test User Credential controller."""

    def setUp(self):
        super(TestCommands, self).setUp()

    @mock.patch('bdocker.utils.load_configuration_from_file')
    @mock.patch("bdocker.modules.load_batch_module")
    def test_create_configuration_error(self, m_batch, m_conf):
        m_conf.side_effect = exceptions.ConfigurationException("")
        self.assertRaises(exceptions.ConfigurationException,
                          commands.CommandController
                          )

    @mock.patch('bdocker.utils.load_configuration_from_file')
    @mock.patch("bdocker.modules.load_batch_module")
    @mock.patch("bdocker.modules.load_credentials_module")
    @mock.patch.object(request.RequestController, "execute_post")
    @mock.patch("bdocker.client.commands.get_user_credentials")
    @mock.patch("bdocker.client.commands.write_user_credentials")
    def test_configuration(self, m_write, m_user, m_post, m_cre,
                           m_batch, m_conf):
        m_conf.return_value = fakes.conf_sge
        admin_token = fakes.admin_token
        m_class_cre = mock.MagicMock()
        m_class_cre.get_admin_token.return_value = admin_token
        m_cre.return_value = m_class_cre
        home_dir = "/foo"
        spool_dir = "/foo"
        job_id = uuid.uuid4().hex
        user = 'peter'
        job_info = {'home': home_dir, 'job_id': job_id,
                    'user_name': user, 'spool': spool_dir}
        m_class_batch = mock.MagicMock()
        m_class_batch.get_job_info.return_value = job_info
        m_batch.return_value = m_class_batch
        user_credentials = {'uid': "", 'gid': "", 'home': home_dir}
        m_user.return_value = user_credentials
        token = uuid.uuid4().hex
        m_post.return_value = token
        controller = commands.CommandController()
        u = controller.configuration()
        self.assertIsNotNone(u)
        self.assertEqual(token, u['token'])
        self.assertIn(home_dir, u['path'])
        token_file = "%s/%s_%s" % (home_dir,
                                   fakes.conf_sge["credentials"]
                                   ["token_client_file"],
                                   job_id)
        self.assertIn(token_file, u['path'])
        expected = {"admin_token": fakes.admin_token,
                    "user_credentials": user_credentials}
        m_post.assert_called_with(path='/configuration',
                                  parameters=expected)

    @mock.patch('bdocker.utils.load_configuration_from_file')
    @mock.patch("bdocker.modules.load_batch_module")
    @mock.patch("bdocker.modules.load_credentials_module")
    @mock.patch("bdocker.client.commands.token_parse")
    @mock.patch.object(request.RequestController, "execute_delete")
    @mock.patch("os.remove")
    def test_clean(self, m_rm, m_del, m_token, m_cre, m_batch, m_conf):
        m_token.return_value = fakes.user_token
        m_conf.return_value = fakes.conf_sge
        admin_token = fakes.admin_token
        m_class_cre = mock.MagicMock()
        m_class_cre.get_admin_token.return_value = admin_token
        m_cre.return_value = m_class_cre
        admin_token = fakes.admin_token
        controller = commands.CommandController()
        controller.clean_environment(None)
        expected = {"admin_token": admin_token,
                    "token": fakes.user_token}
        m_del.assert_called_with(path='/clean',
                                 parameters=expected)

    @mock.patch('bdocker.utils.load_configuration_from_file')
    @mock.patch("bdocker.modules.load_batch_module")
    @mock.patch("bdocker.modules.load_credentials_module")
    @mock.patch("bdocker.client.commands.token_parse")
    @mock.patch.object(request.RequestController, "execute_delete")
    @mock.patch("os.remove")
    def test_clean_token_token(self, m_rm, m_del, m_token, m_cre,
                               m_batch, m_conf):
        m_token.return_value = fakes.user_token
        m_conf.return_value = fakes.conf_sge
        admin_token = fakes.admin_token
        m_class_cre = mock.MagicMock()
        m_class_cre.get_admin_token.return_value = admin_token
        m_class_cre.get_token.return_value = fakes.token_store[
            fakes.user_token
        ]
        m_cre.return_value = m_class_cre
        admin_token = fakes.admin_token
        controller = commands.CommandController()
        controller.clean_environment(fakes.user_token)
        expected = {"admin_token": admin_token,
                    "token": fakes.user_token}
        m_del.assert_called_with(path='/clean',
                                 parameters=expected)

    @mock.patch('bdocker.utils.load_configuration_from_file')
    @mock.patch("bdocker.modules.load_batch_module")
    @mock.patch("bdocker.modules.load_credentials_module")
    def test_clean_admin_err(self, m_cre, m_batch, m_conf):
        m_class_cre = mock.MagicMock()
        exc = exceptions.UserCredentialsException("")
        m_class_cre.get_admin_token.side_effect = exc
        m_cre.return_value = m_class_cre
        controller = commands.CommandController()
        self.assertRaises(exceptions.UserCredentialsException,
                          controller.clean_environment,
                          None
                          )

    @mock.patch('bdocker.utils.load_configuration_from_file')
    @mock.patch("bdocker.modules.load_batch_module")
    @mock.patch("bdocker.modules.load_credentials_module")
    @mock.patch("bdocker.client.commands.token_parse")
    def test_clean_token_err(self, m_token, m_cre, m_batch, m_conf):
        m_class_cre = mock.MagicMock()
        m_class_cre.get_admin_token.return_value = True
        m_cre.return_value = m_class_cre
        controller = commands.CommandController()
        m_token.side_effect = exceptions.UserCredentialsException("")
        self.assertRaises(exceptions.UserCredentialsException,
                          controller.clean_environment,
                          None
                          )

    @mock.patch('bdocker.utils.load_configuration_from_file')
    @mock.patch("bdocker.modules.load_batch_module")
    @mock.patch("bdocker.client.commands.token_parse")
    @mock.patch.object(request.RequestController, "execute_post")
    def test_container_pull(self, m_post, m_token, m_batch, m_conf):
        m_token.return_value = fakes.user_token
        m_conf.return_value = fakes.conf_sge
        home_dir = "/foo"
        spool_dir = "/foo"
        job_id = uuid.uuid4().hex
        user = 'peter'
        job_info = {'home': home_dir, 'job_id': job_id,
                    'user_name': user, 'spool': spool_dir}
        m_class_batch = mock.MagicMock()
        m_class_batch.get_job_info.return_value = job_info
        m_batch.return_value = m_class_batch
        expected = uuid.uuid4().hex
        m_post.return_value = expected
        source = uuid.uuid4().hex
        controller = commands.CommandController()
        results = controller.container_pull(None, source)
        self.assertEqual(expected, results)
        expected_param = {"token": fakes.user_token,
                          "source": source}
        m_post.assert_called_with(path='/pull',
                                  parameters=expected_param)

    @mock.patch('bdocker.utils.load_configuration_from_file')
    @mock.patch("bdocker.modules.load_batch_module")
    @mock.patch("bdocker.client.commands.token_parse")
    @mock.patch.object(request.RequestController, "execute_put")
    def test_container_run(self, m_put, m_token, m_batch, m_conf):
        m_token.return_value = fakes.user_token
        m_conf.return_value = fakes.conf_sge
        home_dir = "/foo"
        spool_dir = "/foo"
        job_id = uuid.uuid4().hex
        user = 'peter'
        job_info = {'home': home_dir, 'job_id': job_id,
                    'user_name': user, 'spool': spool_dir}
        m_class_batch = mock.MagicMock()
        m_class_batch.get_job_info.return_value = job_info
        m_batch.return_value = m_class_batch
        expected = uuid.uuid4().hex
        m_put.return_value = expected
        controller = commands.CommandController()
        image_id = uuid.uuid4().hex
        results = controller.container_run(None, image_id, False, 'ls')
        self.assertEqual(expected, results)

    @mock.patch('bdocker.utils.load_configuration_from_file')
    @mock.patch("bdocker.modules.load_batch_module")
    @mock.patch("bdocker.client.commands.token_parse")
    @mock.patch.object(request.RequestController, "execute_put")
    def test_container_run_2(self, m_put, m_token, m_batch, m_conf):
        m_token.return_value = fakes.user_token
        m_conf.return_value = fakes.conf_sge
        home_dir = "/foo"
        spool_dir = "/foo"
        job_id = uuid.uuid4().hex
        user = 'peter'
        job_info = {'home': home_dir, 'job_id': job_id,
                    'user_name': user, 'spool': spool_dir}
        m_class_batch = mock.MagicMock()
        m_class_batch.get_job_info.return_value = job_info
        m_batch.return_value = m_class_batch
        expected = ['bin', 'etc', 'lib']
        m_put.return_value = expected
        controller = commands.CommandController()
        image_id = uuid.uuid4().hex
        results = controller.container_run(None, image_id, False, 'ls')
        self.assertEqual(expected, results)

    @mock.patch('bdocker.utils.load_configuration_from_file')
    @mock.patch("bdocker.modules.load_batch_module")
    @mock.patch("bdocker.client.commands.token_parse")
    @mock.patch.object(request.RequestController, "execute_get")
    def test_container_list(self, m_get, m_token, m_batch, m_conf):
        m_token.return_value = fakes.user_token
        m_conf.return_value = fakes.conf_sge
        home_dir = "/foo"
        spool_dir = "/foo"
        job_id = uuid.uuid4().hex
        user = 'peter'
        job_info = {'home': home_dir, 'job_id': job_id,
                    'user_name': user, 'spool': spool_dir}
        m_class_batch = mock.MagicMock()
        m_class_batch.get_job_info.return_value = job_info
        m_batch.return_value = m_class_batch
        expected = ["container_1", "container_2"]
        m_get.return_value = expected
        controller = commands.CommandController()
        results = controller.container_list(None)
        self.assertEqual(expected[0], results[0])
        self.assertEqual(expected[1], results[1])

    @mock.patch('bdocker.utils.load_configuration_from_file')
    @mock.patch("bdocker.modules.load_batch_module")
    @mock.patch("bdocker.modules.load_credentials_module")
    @mock.patch("bdocker.client.commands.token_parse")
    @mock.patch.object(request.RequestController, "execute_put")
    def test_notify_accounting(self, m_put, m_token, m_cre, m_batch,
                               m_conf):
        m_token.return_value = fakes.user_token
        m_conf.return_value = fakes.conf_sge
        admin_token = fakes.admin_token
        m_class_cre = mock.MagicMock()
        m_class_cre.get_admin_token.return_value = admin_token
        m_cre.return_value = m_class_cre
        accounting = {"cpu": 1,
                      "mem": 2}
        m_class_bat = mock.MagicMock()
        m_class_bat.create_accounting.return_value = accounting
        m_batch.return_value = m_class_bat
        controller = commands.CommandController()
        out = controller.notify_accounting(None)
        self.assertEqual(fakes.user_token, out)
        expected = {"admin_token": admin_token,
                    "accounting": accounting}
        m_put.assert_called_with(path='/notify_accounting',
                                 parameters=expected)

    @mock.patch('bdocker.utils.load_configuration_from_file')
    @mock.patch("bdocker.modules.load_batch_module")
    @mock.patch("bdocker.client.commands.token_parse")
    @mock.patch.object(request.RequestController, "execute_put")
    def test_copy_to_container(self, m_put, m_token, m_batch, m_conf):
        m_token.return_value = fakes.user_token
        m_conf.return_value = fakes.conf_sge
        home_dir = "/foo"
        spool_dir = "/foo"
        job_id = uuid.uuid4().hex
        user = 'peter'
        job_info = {'home': home_dir, 'job_id': job_id,
                    'user_name': user, 'spool': spool_dir}
        m_class_batch = mock.MagicMock()
        m_class_batch.get_job_info.return_value = job_info
        m_batch.return_value = m_class_batch
        controller = commands.CommandController()
        container_id = uuid.uuid4().hex
        container_path = uuid.uuid4().hex
        host_path = uuid.uuid4().hex
        host_to_container = True
        controller.copy_to_from_container(fakes.user_token,
                                          container_id,
                                          container_path,
                                          host_path,
                                          host_to_container
                                          )
        expected = {"token": fakes.user_token,
                    "container_id": container_id,
                    "container_path": container_path,
                    "host_path": host_path,
                    "host_to_container": host_to_container}
        m_put.assert_called_with(path='/copy',
                                 parameters=expected)

    @mock.patch('bdocker.utils.load_configuration_from_file')
    @mock.patch("bdocker.modules.load_batch_module")
    @mock.patch("bdocker.client.commands.token_parse")
    @mock.patch.object(request.RequestController, "execute_put")
    def test_delete_container(self, m_put, m_token, m_batch, m_conf):
        m_token.return_value = fakes.user_token
        m_conf.return_value = fakes.conf_sge
        home_dir = "/foo"
        spool_dir = "/foo"
        job_id = uuid.uuid4().hex
        user = 'peter'
        job_info = {'home': home_dir, 'job_id': job_id,
                    'user_name': user, 'spool': spool_dir}
        m_class_batch = mock.MagicMock()
        m_class_batch.get_job_info.return_value = job_info
        m_batch.return_value = m_class_batch
        controller = commands.CommandController()
        containers = [uuid.uuid4().hex, uuid.uuid4().hex]
        controller.container_delete(None, containers)
        expected = {"token": fakes.user_token,
                    "container_id": containers,
                    "force": False}
        m_put.assert_called_with(path='/rm',
                                 parameters=expected)

    @mock.patch('bdocker.utils.load_configuration_from_file')
    @mock.patch("bdocker.modules.load_batch_module")
    @mock.patch("bdocker.client.commands.token_parse")
    @mock.patch.object(request.RequestController, "execute_put")
    def test_delete_container_force(self, m_put, m_token, m_batch,
                                    m_conf):
        m_token.return_value = fakes.user_token
        m_conf.return_value = fakes.conf_sge
        home_dir = "/foo"
        spool_dir = "/foo"
        job_id = uuid.uuid4().hex
        user = 'peter'
        job_info = {'home': home_dir, 'job_id': job_id,
                    'user_name': user, 'spool': spool_dir}
        m_class_batch = mock.MagicMock()
        m_class_batch.get_job_info.return_value = job_info
        m_batch.return_value = m_class_batch
        controller = commands.CommandController()
        containers = [uuid.uuid4().hex, uuid.uuid4().hex]
        controller.container_delete(None, containers, True)
        expected = {"token": fakes.user_token,
                    "container_id": containers,
                    "force": True}
        m_put.assert_called_with(path='/rm',
                                 parameters=expected)

    @mock.patch('bdocker.utils.load_configuration_from_file')
    @mock.patch("bdocker.modules.load_batch_module")
    @mock.patch("bdocker.client.commands.token_parse")
    @mock.patch.object(request.RequestController, "execute_get")
    def test_inpect_container(self, m_get, m_token, m_batch, m_conf):
        m_token.return_value = fakes.user_token
        m_conf.return_value = fakes.conf_sge
        home_dir = "/foo"
        spool_dir = "/foo"
        job_id = uuid.uuid4().hex
        user = 'peter'
        job_info = {'home': home_dir, 'job_id': job_id,
                    'user_name': user, 'spool': spool_dir}
        m_class_batch = mock.MagicMock()
        m_class_batch.get_job_info.return_value = job_info
        m_batch.return_value = m_class_batch
        controller = commands.CommandController()
        container_id = uuid.uuid4().hex
        m_get.return_value = fakes.container1
        result = controller.container_inspect(None, container_id)
        self.assertEqual(fakes.container1, result)
        expected = {"token": fakes.user_token,
                    "container_id": container_id}
        m_get.assert_called_with(path='/inspect',
                                 parameters=expected)

    @mock.patch('bdocker.utils.load_configuration_from_file')
    @mock.patch("bdocker.modules.load_batch_module")
    @mock.patch("bdocker.client.commands.token_parse")
    @mock.patch.object(request.RequestController, "execute_get")
    def test_logs_container(self, m_get, m_token, m_batch, m_conf):
        m_token.return_value = fakes.user_token
        m_conf.return_value = fakes.conf_sge
        home_dir = "/foo"
        spool_dir = "/foo"
        job_id = uuid.uuid4().hex
        user = 'peter'
        job_info = {'home': home_dir, 'job_id': job_id,
                    'user_name': user, 'spool': spool_dir}
        m_class_batch = mock.MagicMock()
        m_class_batch.get_job_info.return_value = job_info
        m_batch.return_value = m_class_batch
        controller = commands.CommandController()
        container_id = uuid.uuid4().hex
        m_get.return_value = fakes.container1
        result = controller.container_logs(None, container_id)
        self.assertEqual(fakes.container1, result)
        expected = {"token": fakes.user_token,
                    "container_id": container_id}
        m_get.assert_called_with(path='/logs',
                                 parameters=expected)
