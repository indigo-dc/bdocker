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

import os
import uuid

import mock
import testtools

from bdocker.client.controller import commands
from bdocker.client.controller import request
from bdocker.common import exceptions
from bdocker.common.modules import batch

os.environ['BDOCKER_CONF_FILE'] = "/home/jorge/Dropbox/INDIGO_DOCKER/bdocker/bdocker/" \
                                  "common/configure_bdocker.cfg"

class TestCommands(testtools.TestCase):
    """Test User Credential controller."""

    @mock.patch('bdocker.client.controller.utils.load_configuration')
    def setUp(self, m):
        super(TestCommands, self).setUp()
        self.job_id = uuid.uuid4().hex
        m.return_value = {'token_store':'/foo',
                          'endpoint': 'http://foo',
                          'token_file': '.bdocker_token',
                          'job_id': self.job_id
                          }
        self.control = commands.CommandController()


    @mock.patch('bdocker.common.utils.load_configuration_from_file')
    def test_create_configuration_error(self, m):
        conf = {"token_file"}
        m.return_value = conf
        self.assertRaises(exceptions.ConfigurationException,
                          commands.CommandController
                          )

    @mock.patch.object(request.RequestController, "execute_post")
    @mock.patch("bdocker.client.controller.utils.get_user_credentials")
    @mock.patch("bdocker.client.controller.utils.write_user_credentials")
    @mock.patch("bdocker.client.controller.utils.get_admin_token")
    def test_create_credentials_token_error(self, m_ad, m_write, m_u, m_post):
        home_dir = "/foo"
        m_u.return_value = {'uid': "", 'gid': "", 'home': home_dir}
        m_post.side_effect = exceptions.UserCredentialsException('')
        self.assertRaises(exceptions.UserCredentialsException,
                          self.control.create_credentials,
                          1)

    @mock.patch.object(request.RequestController, "execute_post")
    @mock.patch("bdocker.client.controller.utils.get_user_credentials")
    @mock.patch("bdocker.client.controller.utils.write_user_credentials")
    @mock.patch("bdocker.client.controller.utils.get_admin_token")
    @mock.patch.object(batch.SGEController, "get_job_info")
    def test_create_credentials(self, m_conf, m_ad, m_write, m_u, m_post):
        admin_token = uuid.uuid4().hex
        home_dir = "/foo"
        job_id = '88'
        spool = "/faa"
        user = 'peter'
        m_conf.return_value = {'home': home_dir,
                               'job_id': job_id,
                               'spool': spool,
                               'user': user}
        m_u.return_value = {'uid': "", 'gid': "", 'home': home_dir}
        m_post.return_value = admin_token
        controller = commands.CommandController()
        u = controller.create_credentials()
        self.assertIsNotNone(u)
        self.assertEqual(admin_token, u['token'])
        self.assertIn(home_dir, u['path'])

    @mock.patch.object(request.RequestController, "execute_post")
    @mock.patch("bdocker.client.controller.utils.get_user_credentials")
    @mock.patch("bdocker.client.controller.utils.write_user_credentials")
    @mock.patch("bdocker.client.controller.utils.get_admin_token")
    @mock.patch.object(batch.SGEController, "get_job_info")
    def test_create_credentials_with_job(self, m_conf, m_ad, m_write, m_u, m_post):
        admin_token = uuid.uuid4().hex
        token = uuid.uuid4().hex
        home_dir = "/foo"
        spool = "/faa"
        job_id = 8934
        user = 'peter'
        m_conf.return_value = {'home': home_dir,
                               'job_id': job_id,
                                'spool': spool,
                               'user': user}
        user_credentials = {'uid': "", 'gid': "", 'home': home_dir}
        m_u.return_value = user_credentials
        m_post.return_value = token
        m_ad.return_value = admin_token
        controller = commands.CommandController()
        u = controller.create_credentials(1000, job_id)
        self.assertIsNotNone(u)
        self.assertEqual(token, u['token'])
        self.assertIn(home_dir, u['path'])
        token_file = "%s/.bdocker_token_%s" % (home_dir, job_id)
        self.assertIn(token_file, u['path'])
        self.assertIn('job', user_credentials)
        expected = {"admin_token": admin_token,
                    "user_credentials": user_credentials}
        m_post.assert_called_with(path='/credentials',
                                 parameters=expected)

    @mock.patch.object(request.RequestController, "execute_post")
    @mock.patch("bdocker.client.controller.utils.token_parse")
    def test_container_pull(self, m_t, m):
        m_t.return_value = uuid.uuid4().hex
        image_id = uuid.uuid4().hex
        source = "foo"
        m.return_value = image_id
        results = self.control.container_pull(None, source)
        self.assertEqual(image_id, results)

    @mock.patch.object(request.RequestController, "execute_put")
    @mock.patch("bdocker.client.controller.utils.token_parse")
    def test_container_run(self, m_t, m):
        m_t.return_value = uuid.uuid4().hex
        image_id = uuid.uuid4().hex
        container_id = uuid.uuid4().hex
        err = None
        m.return_value = container_id
        results = self.control.container_run(None, image_id, False, 'ls')
        self.assertEqual(container_id, results)

    @mock.patch.object(request.RequestController, "execute_put")
    @mock.patch("bdocker.client.controller.utils.token_parse")
    def test_container_run_2(self, m_t, m):
        m_t.return_value = uuid.uuid4().hex
        image_id = uuid.uuid4().hex
        container_id = uuid.uuid4().hex
        out = ['bin', 'etc', 'lib']
        m.return_value = ['bin', 'etc', 'lib']
        results = self.control.container_run(None, image_id, False, 'ls')
        self.assertEqual(out, results)

    @mock.patch.object(request.RequestController, "execute_get")
    @mock.patch("bdocker.client.controller.utils.token_parse")
    def test_container_list(self, m_t, m):
        m_t.return_value = uuid.uuid4().hex
        containers = ["container_1", "container_2"]
        m.return_value = containers
        results = self.control.container_list(None)
        self.assertEqual(containers[0], results[0])
        self.assertEqual(containers[1], results[1])

    @mock.patch.object(request.RequestController, "execute_put")
    @mock.patch("bdocker.client.controller.utils.get_admin_token")
    @mock.patch("bdocker.client.controller.utils.token_parse")
    def test_batch_config(self, m_t, m_ad, m_put):
        token = uuid.uuid4().hex
        admin_token = uuid.uuid4().hex
        m_t.return_value = token
        m_ad.return_value = admin_token
        self.control.batch_config(None)
        expected = {"admin_token": admin_token,
                    "token": token}
        m_put.assert_called_with(path='/batchconf',
                                 parameters=expected)

    @mock.patch.object(request.RequestController, "execute_put")
    @mock.patch("bdocker.client.controller.utils.get_admin_token")
    @mock.patch("bdocker.client.controller.utils.token_parse")
    def test_batch_config_admin_err(self, m_t, m_ad, m_put):
        m_ad.side_effect = exceptions.UserCredentialsException("")
        self.assertRaises(exceptions.UserCredentialsException,
                          self.control.batch_config,
                          None)

    @mock.patch.object(request.RequestController, "execute_put")
    @mock.patch("bdocker.client.controller.utils.get_admin_token")
    @mock.patch("bdocker.client.controller.utils.token_parse")
    def test_batch_config_token_err(self, m_t, m_ad, m_put):
        m_t.side_effect = exceptions.UserCredentialsException("")
        self.assertRaises(exceptions.UserCredentialsException,
                          self.control.batch_config,
                          None)

    @mock.patch.object(request.RequestController, "execute_delete")
    @mock.patch("bdocker.client.controller.utils.get_admin_token")
    @mock.patch("bdocker.client.controller.utils.token_parse")
    def test_batch_clean(self, m_t, m_ad, m_del):
        token = uuid.uuid4().hex
        admin_token = uuid.uuid4().hex
        m_t.return_value = token
        m_ad.return_value = admin_token
        containers = ["container_1", "container_2"]
        m_del.return_value = containers
        self.control.batch_clean(None)
        expected = {"admin_token": admin_token,
                    "token": token}
        m_del.assert_called_with(path='/batchclean',
                                 parameters=expected)

    @mock.patch.object(request.RequestController, "execute_delete")
    @mock.patch("bdocker.client.controller.utils.get_admin_token")
    @mock.patch("bdocker.client.controller.utils.token_parse")
    def test_batch_clean_admin_err(self, m_t, m_ad, m_del):
        m_ad.side_effect = exceptions.UserCredentialsException("")
        self.assertRaises(exceptions.UserCredentialsException,
                          self.control.batch_clean,
                          None)

    @mock.patch.object(request.RequestController, "execute_delete")
    @mock.patch("bdocker.client.controller.utils.get_admin_token")
    @mock.patch("bdocker.client.controller.utils.token_parse")
    def test_batch_clean_token_err(self, m_t, m_ad, m_del):
        m_t.side_effect = exceptions.UserCredentialsException("")
        self.assertRaises(exceptions.UserCredentialsException,
                          self.control.batch_clean,
                          None)

    @mock.patch.object(request.RequestController, "execute_post")
    @mock.patch("bdocker.client.controller.utils.get_user_credentials")
    @mock.patch("bdocker.client.controller.utils.write_user_credentials")
    @mock.patch("bdocker.client.controller.utils.get_admin_token")
    @mock.patch.object(batch.SGEController, "get_job_info")
    def test_full_configuration(self, m_conf, m_ad, m_write, m_u, m_post):
        admin_token = uuid.uuid4().hex
        token = uuid.uuid4().hex
        home_dir = "/foo"
        spool = "/faa"
        job_id = 8934
        user = 'peter'
        m_conf.return_value = {'home': home_dir,
                               'job_id': job_id,
                                'spool': spool,
                               'user': user}
        user_credentials = {'uid': "", 'gid': "", 'home': home_dir}
        m_u.return_value = user_credentials
        m_post.return_value = token
        m_ad.return_value = admin_token
        controller = commands.CommandController()
        u = controller.configuration(1000, job_id)
        self.assertIsNotNone(u)
        self.assertEqual(token, u['token'])
        self.assertIn(home_dir, u['path'])
        token_file = "%s/.bdocker_token_%s" % (home_dir, job_id)
        self.assertIn(token_file, u['path'])
        self.assertIn('job', user_credentials)
        expected = {"admin_token": admin_token,
                    "user_credentials": user_credentials}
        m_post.assert_called_with(path='/configuration',
                                 parameters=expected)

    # def test_crendentials(self):
    #     results = self.control.create_credentials(1000)
    #     self.assertIsNotNone(results)

        # CREATE CONTAINER {'Id': '8a61192da2b3bb2d922875585e29b74ec0dc4e0117fcbf84c962204e97564cd7', 'Warnings': None}
