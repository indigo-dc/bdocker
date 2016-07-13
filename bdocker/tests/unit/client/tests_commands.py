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
import uuid

import mock
import testtools

from bdocker.client import commands
from bdocker import exceptions
from bdocker.modules import batch
from bdocker.modules import credentials
from bdocker.modules import request
from bdocker.tests import fakes


class TestCommands(testtools.TestCase):
    """Test User Credential controller."""

    def setUp(self):
        super(TestCommands, self).setUp()
        self.job_id = uuid.uuid4().hex
        with mock.patch(
                'bdocker.utils.load_configuration_from_file',
                return_value=fakes.conf_sge):
            with mock.patch("bdocker.utils.read_yaml_file",
                            return_value=copy.deepcopy(fakes.token_store)):
                self.control = commands.CommandController()

    @mock.patch('bdocker.utils.load_configuration_from_file')
    def test_create_configuration_error(self, m):
        conf = {"token_file"}
        m.return_value = conf
        self.assertRaises(exceptions.ConfigurationException,
                          commands.CommandController
                          )

    @mock.patch.object(request.RequestController, "execute_post")
    @mock.patch("bdocker.client.commands.get_user_credentials")
    @mock.patch("bdocker.client.commands.write_user_credentials")
    @mock.patch.object(credentials.UserController, "get_admin_token")
    @mock.patch.object(batch.SGEController, "get_job_info")
    def test_configuration_token_error(self, m_env, m_ad, m_write,
                                       m_u, m_post):
        home_dir = "/foo"
        m_u.return_value = {'uid': "", 'gid': "", 'home': home_dir}
        m_post.side_effect = exceptions.UserCredentialsException('')
        self.assertRaises(exceptions.UserCredentialsException,
                          self.control.configuration,
                          1)

    @mock.patch.object(request.RequestController, "execute_post")
    @mock.patch("bdocker.client.commands.get_user_credentials")
    @mock.patch("bdocker.client.commands.write_user_credentials")
    @mock.patch.object(credentials.UserController, "get_admin_token")
    @mock.patch.object(batch.SGEController, "get_job_info")
    def test_configuration(self, m_conf, m_ad, m_write, m_u, m_post):
        admin_token = uuid.uuid4().hex
        home_dir = "/foo"
        m_u.return_value = {'uid': "", 'gid': "", 'home': home_dir}
        m_post.return_value = admin_token
        with mock.patch('bdocker.utils.load_configuration_from_file',
                        return_value=fakes.conf_sge):
            with mock.patch("bdocker.utils.read_yaml_file",
                            return_value=copy.deepcopy(fakes.token_store)):
                controller = commands.CommandController()
        u = controller.configuration()
        self.assertIsNotNone(u)
        self.assertEqual(admin_token, u['token'])
        self.assertIn(home_dir, u['path'])

    @mock.patch.object(request.RequestController, "execute_post")
    @mock.patch("bdocker.client.commands.get_user_credentials")
    @mock.patch("bdocker.client.commands.write_user_credentials")
    @mock.patch.object(credentials.UserController, "get_admin_token")
    @mock.patch.object(batch.SGEController, "get_job_info")
    def test_configuration_with_job(self, m_env, m_ad, m_write, m_u, m_post):
        token = uuid.uuid4().hex
        home_dir = "/foo"
        spool_dir = "/foo"
        job_id = 8934
        user = 'peter'
        m_env.return_value = {'home': home_dir,
                              'job_id': job_id,
                              'user_name': user,
                              'spool': spool_dir,
                              }
        user_credentials = {'uid': "", 'gid': "", 'home': home_dir}
        m_u.return_value = user_credentials
        m_post.return_value = token
        m_ad.return_value = fakes.admin_token
        with mock.patch('bdocker.utils.load_configuration_from_file',
                        return_value=fakes.conf_sge):
            with mock.patch("bdocker.utils.read_yaml_file",
                            return_value=copy.deepcopy(fakes.token_store)):
                controller = commands.CommandController()
        u = controller.configuration(1000, job_id)
        self.assertIsNotNone(u)
        self.assertEqual(token, u['token'])
        self.assertIn(home_dir, u['path'])
        token_file = "%s/.bdocker_token_%s" % (home_dir, job_id)
        self.assertIn(token_file, u['path'])
        self.assertIn('job', user_credentials)
        expected = {"admin_token": fakes.admin_token,
                    "user_credentials": user_credentials}
        m_post.assert_called_with(path='/configuration',
                                  parameters=expected)

    @mock.patch.object(request.RequestController, "execute_post")
    @mock.patch("bdocker.client.commands.token_parse")
    @mock.patch.object(batch.SGEController, "get_job_info")
    def test_container_pull(self, m_env, m_t, m):
        m_t.return_value = uuid.uuid4().hex
        image_id = uuid.uuid4().hex
        source = "foo"
        m.return_value = image_id
        results = self.control.container_pull(None, source)
        self.assertEqual(image_id, results)

    @mock.patch.object(request.RequestController, "execute_put")
    @mock.patch("bdocker.client.commands.token_parse")
    @mock.patch.object(batch.SGEController, "get_job_info")
    def test_container_run(self, m_env, m_t, m):
        m_t.return_value = uuid.uuid4().hex
        image_id = uuid.uuid4().hex
        container_id = uuid.uuid4().hex
        m.return_value = container_id
        results = self.control.container_run(None, image_id, False, 'ls')
        self.assertEqual(container_id, results)

    @mock.patch.object(request.RequestController, "execute_put")
    @mock.patch("bdocker.client.commands.token_parse")
    @mock.patch.object(batch.SGEController, "get_job_info")
    def test_container_run_2(self, m_env, m_t, m):
        m_t.return_value = uuid.uuid4().hex
        image_id = uuid.uuid4().hex
        out = ['bin', 'etc', 'lib']
        m.return_value = ['bin', 'etc', 'lib']
        results = self.control.container_run(None, image_id, False, 'ls')
        self.assertEqual(out, results)

    @mock.patch.object(request.RequestController, "execute_get")
    @mock.patch("bdocker.client.commands.token_parse")
    @mock.patch.object(batch.SGEController, "get_job_info")
    def test_container_list(self, m_env, m_t, m):
        m_t.return_value = uuid.uuid4().hex
        containers = ["container_1", "container_2"]
        m.return_value = containers
        results = self.control.container_list(None)
        self.assertEqual(containers[0], results[0])
        self.assertEqual(containers[1], results[1])

    @mock.patch.object(request.RequestController, "execute_delete")
    @mock.patch.object(credentials.UserController, "get_admin_token")
    @mock.patch("bdocker.client.commands.token_parse")
    @mock.patch("os.remove")
    @mock.patch.object(batch.SGEController, "get_job_info")
    def test_clean(self, m_env, m_rm, m_t, m_ad, m_del):
        token = uuid.uuid4().hex
        admin_token = fakes.admin_token
        m_t.return_value = token
        m_ad.return_value = admin_token
        containers = ["container_1", "container_2"]
        m_del.return_value = containers
        self.control.clean_environment(None)
        expected = {"admin_token": admin_token,
                    "token": token}
        m_del.assert_called_with(path='/clean',
                                 parameters=expected)

    @mock.patch.object(request.RequestController, "execute_delete")
    @mock.patch.object(credentials.UserController, "get_admin_token")
    @mock.patch("bdocker.client.commands.token_parse")
    def test_clean_admin_err(self, m_t, m_ad, m_del):
        m_ad.side_effect = exceptions.UserCredentialsException("")
        self.assertRaises(exceptions.UserCredentialsException,
                          self.control.clean_environment,
                          None
                          )

    @mock.patch.object(request.RequestController, "execute_delete")
    @mock.patch.object(credentials.UserController, "get_admin_token")
    @mock.patch("bdocker.client.commands.token_parse")
    @mock.patch.object(batch.SGEController, "get_job_info")
    def test_clean_token_err(self, m_env, m_t, m_ad, m_del):
        m_t.side_effect = exceptions.UserCredentialsException("")
        self.assertRaises(exceptions.UserCredentialsException,
                          self.control.clean_environment,
                          None)

    @mock.patch.object(request.RequestController, "execute_put")
    @mock.patch.object(credentials.UserController, "get_admin_token")
    @mock.patch("bdocker.client.commands.token_parse")
    @mock.patch.object(batch.SGEController, "create_accounting")
    @mock.patch.object(batch.SGEController, "get_job_info")
    def test_notify_accounting(self, m_env, m_acc, m_t, m_ad, m_del):
        token = uuid.uuid4().hex
        admin_token = uuid.uuid4().hex
        m_t.return_value = token
        m_ad.return_value = admin_token
        accounting = {"cpu": 1,
                      "mem": 2}
        m_acc.return_value = accounting
        out = self.control.notify_accounting(None)
        self.assertEqual(token, out)
        expected = {"admin_token": admin_token,
                    "accounting": accounting}
        m_del.assert_called_with(path='/notify_accounting',
                                 parameters=expected)

    @mock.patch.object(request.RequestController, "execute_put")
    @mock.patch("bdocker.client.commands.token_parse")
    @mock.patch.object(batch.SGEController, "get_job_info")
    def test_copy_to_container(self, m_env, m_token, m_put):
        token = uuid.uuid4().hex
        container_id = uuid.uuid4().hex
        container_path = uuid.uuid4().hex
        host_path = uuid.uuid4().hex
        host_to_container = True
        m_token.return_value = token
        self.control.copy_to_from_container(token, container_id,
                                            container_path,
                                            host_path,
                                            host_to_container
                                            )
        expected = {"token": token,
                    "container_id": container_id,
                    "container_path": container_path,
                    "host_path": host_path,
                    "host_to_container": host_to_container}
        m_put.assert_called_with(path='/copy',
                                 parameters=expected)
