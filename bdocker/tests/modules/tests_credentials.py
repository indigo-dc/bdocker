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

import os
import uuid

import mock
import testtools

from bdocker import exceptions
from bdocker.modules import credentials


def create_parameters():
    parameters = {
        "token": "tokennnnnn",
        "user_credentials":
            {'uid': 'uuuuuuuuuuiiiidddddd',
             'gid': 'gggggggggguuuiiidd',
             'home': '/home',
             }
    }
    return parameters


class TestUserCredentials(testtools.TestCase):
    """Test User Credential controller."""

    def setUp(self):
        super(TestUserCredentials, self).setUp()
        self.path = os.path.join(
            os.path.dirname(__file__),
            'fake_token_store.yml')
        self.control = credentials.UserController(self.path)

    def test_token_store(self):
        user_info = self.control._get_token_from_cache("token1")
        self.assertEqual(3, user_info.__len__())

    def test_prolog_token(self):
        user_info = self.control._get_token_from_cache("prolog")
        self.assertEqual(1, user_info.__len__())
        self.assertEqual("token_prolog", user_info['token'])

    @mock.patch('bdocker.utils.check_user_credentials')
    def test_authenticate(self, m):
        t = self.control._get_token_from_cache(
            "prolog")['token']
        u = create_parameters()['user_credentials']
        token = self.control.authenticate(admin_token=t,
                                          session_data=u)
        self.assertIsNotNone(token)
        token_info = self.control._get_token_from_cache(token)
        self.assertEqual(u['uid'], token_info['uid'])
        self.assertEqual(u['home'], token_info['home'])
        self.assertEqual(u['gid'], token_info['gid'])
        self.assertNotIn('job', token_info)
        self.control.remove_token_from_cache(token)

    @mock.patch('bdocker.utils.check_user_credentials')
    def test_authenticate_with_job(self, m):
        jobid = uuid.uuid4().hex
        spool = uuid.uuid4().hex
        t = self.control._get_token_from_cache(
            "prolog")['token']
        u = create_parameters()['user_credentials']
        u.update({'job': {'job_id': jobid,
                          'spool': spool}
                  })
        token = self.control.authenticate(admin_token=t,
                                          session_data=u)
        self.assertIsNotNone(token)
        job_info = self.control.get_job_from_token(token)
        self.assertEqual(jobid, job_info['job_id'])
        self.assertEqual(spool, job_info['spool'])
        self.assertNotIn('cgroup', job_info)
        self.control.remove_token_from_cache(token)

    # @mock.patch('bdocker.utils.check_user_credentials')
    # def test_authenticate_with_job_accouting_info(self, m):
    #     jobid = uuid.uuid4().hex
    #     spool = uuid.uuid4().hex
    #     user = uuid.uuid4().hex
    #     qname = uuid.uuid4().hex
    #     logname = uuid.uuid4().hex
    #     hostname = uuid.uuid4().hex
    #     job_name = uuid.uuid4().hex
    #     account = uuid.uuid4().hex
    #     t = self.control._get_token_from_cache(
    #         "prolog")['token']
    #     u = create_parameters()['user_credentials']
    #     u.update({'job': {'id': jobid,
    #                       'user_name': user,
    #                       'spool': spool,
    #                       'queue_name': qname,
    #                       'host_name': hostname,
    #                       'log_name': logname,
    #                       'job_name': job_name,
    #                       'account_name': account}
    #               }
    #              )
    #     token = self.control.authenticate(admin_token=t,
    #                                       session_data=u)
    #     self.assertIsNotNone(token)
    #     job_info = self.control.get_job_from_token(token)
    #     self.assertEqual(jobid, job_info['id'])
    #     self.assertEqual(spool, job_info['spool'])
    #     self.assertEqual(user, job_info['user_name'])
    #     self.assertEqual(qname, job_info['queue_name'])
    #     self.assertEqual(hostname, job_info['host_name'])
    #     self.assertEqual(job_name, job_info['job_name'])
    #     self.assertEqual(logname, job_info['log_name'])
    #     self.assertEqual(account, job_info['account_name'])
    #     self.assertNotIn('cgroup', job_info)
    #     self.control.remove_token_from_cache(token)

    @mock.patch('bdocker.utils.check_user_credentials')
    def test_authenticate_with_job_batch_info(self, m):
        jobid = uuid.uuid4().hex
        spool = uuid.uuid4().hex
        cgroup = uuid.uuid4().hex
        batch_info = {"cgroup": cgroup}
        t = self.control._get_token_from_cache(
            "prolog")['token']
        u = create_parameters()['user_credentials']
        u.update({'job': {'job_id': jobid,
                          'spool': spool}
                  })
        token = self.control.authenticate(admin_token=t,
                                          session_data=u)
        self.control.set_token_batch_info(token, batch_info)
        job_info = self.control.get_job_from_token(token)
        self.assertEqual(jobid, job_info['job_id'])
        self.assertEqual(spool, job_info['spool'])
        self.assertEqual(cgroup, job_info['cgroup'])
        self.control.remove_token_from_cache(token)
        self.assertIsNotNone(token)

    @mock.patch('bdocker.utils.check_user_credentials')
    def test_authenticate_save_file(self, m):
        t = self.control._get_token_from_cache("prolog")['token']
        u = create_parameters()['user_credentials']
        token = self.control.authenticate(admin_token=t,
                                          session_data=u)
        self.assertIsNotNone(token)
        new_controller = credentials.UserController(self.path)
        user_info1 = new_controller._get_token_from_cache(token)
        self.assertEqual(3, user_info1.__len__())
        new_controller.remove_token_from_cache(token)
        self.assertRaises(exceptions.UserCredentialsException,
                          new_controller._get_token_from_cache,
                          token)

    def test_authorize(self):
        t = 'token2'
        ath = self.control.authorize(t)
        self.assertIsNotNone(ath)
        self.assertIsNotNone(ath['uid'])
        self.assertIsNotNone(ath['home_dir'])
        self.assertIsNotNone(ath['gid'])
        self.assertIsNotNone(ath['containers'])
        self.assertIsNotNone(ath['images'])
        self.assertIsNotNone(ath['jobid'])

    def test_authorize_err(self):
        t = 'token'
        self.assertRaises(exceptions.UserCredentialsException,
                          self.control.authorize, t)

    def test_authorize_containers(self):
        t = 'token2'
        c = 'cotainer1'
        ath = self.control.authorize_container(
            token=t,
            container_id=c)
        self.assertIs(c, ath)

    def test_authorize_container_err(self):
        t = 'token'
        c = '84848'
        self.assertRaises(exceptions.UserCredentialsException,
                          self.control.authorize_container, t, c)

    def test_add_container(self):
        token = "token2"
        c_id = "container3"
        token_info = self.control._get_token_from_cache(token)
        self.assertIsNotNone(token_info['containers'])
        self.assertEqual(2,
                         token_info['containers'].__len__())
        self.control.add_container(token, c_id)
        self.assertIsNotNone(
            token_info['containers'])
        self.assertEqual(3,
                         token_info['containers'].__len__())
        self.control.remove_container(token, c_id)
        self.assertIsNotNone(token_info['containers'])
        self.assertEqual(2,
                         token_info['containers'].__len__())

    def test_add_container_err(self):
        pass

    def test_create_remove_container(self):
        token = "token1"
        c_id = "container1"
        token_info = self.control._get_token_from_cache(token)
        self.assertNotIn('containers', token_info)
        self.control.add_container(token, c_id)
        self.assertIsNotNone(token_info['containers'])
        self.assertEqual(1,
                         token_info['containers'].__len__())
        self.control.remove_container(token, c_id)
        self.assertNotIn('containers', token_info)

    def test_authorize_images(self):
        t = 'token2'
        c = 'image1'
        ath = self.control.authorize_image(
            token=t,
            image_id=c)
        self.assertIs(True, ath)

    def test_authorize_image_err(self):
        t = 'token'
        c = '84848'
        self.assertRaises(exceptions.UserCredentialsException,
                          self.control.authorize_image, t, c)

    def test_add_image(self):
        token = "token2"
        image_id = "image2"
        token_info = self.control._get_token_from_cache(token)
        self.assertIsNotNone(token_info['images'])
        self.assertEqual(1,
                         token_info['images'].__len__())
        self.control.add_image(token, image_id)
        self.assertIsNotNone(
            token_info['images'])
        self.assertEqual(2,
                         token_info['images'].__len__())
        self.control.remove_image(token, image_id)
        self.assertIsNotNone(token_info['images'])
        self.assertEqual(1,
                         token_info['images'].__len__())

    def test_create_remove_image(self):
        token = "token1"
        c_id = "image1"
        token_info = self.control._get_token_from_cache(token)
        self.assertNotIn('images', token_info)
        self.control.add_image(token, c_id)
        self.assertIsNotNone(token_info['images'])
        self.assertEqual(1,
                         token_info['images'].__len__())
        self.control.remove_image(token, c_id)
        self.assertNotIn('images', token_info)

    def test_list_containers(self):
        t = 'token2'
        list_containers = self.control.list_containers(
            token=t)
        self.assertIsNotNone(list_containers)

    def test_authorize_admin(self):
        pass

    def remove_container(self):
        pass

    def remove_container_err(self):
        pass

    def test_list_containers(self):
        pass

    @mock.patch.object(credentials.UserController,
                       "_get_token_from_cache")
    @mock.patch("bdocker.utils.validate_directory")
    def test_authorize_directory(self, m_val, m_token):
        token = uuid.uuid4().hex
        uid = uuid.uuid4().hex
        gid = uuid.uuid4().hex
        jobid = uuid.uuid4().hex
        spool = uuid.uuid4().hex
        cgroup = uuid.uuid4().hex
        home = uuid.uuid4().hex
        token_info = {"home": home,
                      "uid": uid,
                      "gid": gid,
                      "job": {
                          "id": jobid,
                          "cgroup": cgroup,
                          "spool": spool}
                      }
        m_token.return_value = token_info
        out = self.control.authorize_directory(token, None)
        self.assertEqual(uid, out["uid"])
        self.assertEqual(gid, out["gid"])

    @mock.patch.object(credentials.UserController,
                       "_get_token_from_cache")
    @mock.patch("bdocker.utils.validate_directory")
    def test_authorize_directory_err(self, m_val, m_token):
        token = uuid.uuid4().hex
        jobid = uuid.uuid4().hex
        spool = uuid.uuid4().hex
        cgroup = uuid.uuid4().hex
        home = uuid.uuid4().hex
        token_info = {"home": home,
                      "job": {
                          "id": jobid,
                          "cgroup": cgroup,
                          "spool": spool}
                      }
        m_token.return_value = token_info
        m_val.side_effect = exceptions.UserCredentialsException("")
        self.assertRaises(exceptions.UserCredentialsException,
                          self.control.authorize_directory,
                          token, None)

    def test_update_token(self):
        pass

    def test_set_token(self):
        pass

    def test_get_token(self):
        pass

    @mock.patch.object(credentials.UserController, "_get_token_from_cache")
    def test_get_job_from_token(self, m_gt):
        uid = uuid.uuid4().hex
        jobid = uuid.uuid4().hex
        spool = uuid.uuid4().hex
        cgroup = uuid.uuid4().hex
        token_info = {"job": {
            "job_id": jobid,
            "cgroup": cgroup,
            "spool": spool}
        }
        m_gt.return_value = token_info
        result = self.control.get_job_from_token(uid)
        self.assertEqual(jobid, result['job_id'])
        self.assertEqual(cgroup, result['cgroup'])
        self.assertEqual(spool, result['spool'])

    @mock.patch.object(credentials.UserController, "_get_token_from_cache")
    def test_get_job_from_token_err(self, m_gt):
        m_gt.side_effect = exceptions.UserCredentialsException("")
        self.assertRaises(exceptions.UserCredentialsException,
                          self.control.get_job_from_token,
                          None)

    @mock.patch.object(credentials.UserController, "_update_token")
    @mock.patch.object(credentials.UserController, "_get_token_from_cache")
    def test_update_job(self, m_get, m_update):
        token = uuid.uuid4().hex
        jobid = uuid.uuid4().hex
        spool = uuid.uuid4().hex
        cgroup = uuid.uuid4().hex
        token_info = {"job": {
            "id": jobid,
            "cgroup": cgroup,
            "spool": spool}
        }
        m_get.return_value = token_info
        accounting = {"cpu": 33,
                      "mem": 11}
        job = token_info["job"]
        job.update(accounting)
        token_2 = self.control.update_job(token, job)
        self.assertEqual(accounting["cpu"], token_2['job']["cpu"])
