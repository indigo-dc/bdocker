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

from bdocker import exceptions
from bdocker.modules import credentials
from bdocker.tests import fakes


class TestUserCredentials(testtools.TestCase):
    """Test User Credential controller."""

    def setUp(self):
        super(TestUserCredentials, self).setUp()
        self.token_store = copy.deepcopy(fakes.token_store)
        with mock.patch("bdocker.utils.read_yaml_file",
                        return_value=self.token_store):
            self.control = credentials.TokenController(None)

    def test_token_store(self):
        user_info = self.control._get_token_from_cache(
            fakes.user_token
        )
        self.assertEqual(6, user_info.__len__())

    def test_prolog_token(self):
        user_info = self.control._get_token_from_cache("prolog")
        self.assertEqual(1, user_info.__len__())
        self.assertEqual(fakes.admin_token, user_info['token'])

    @mock.patch('bdocker.utils.check_user_credentials')
    def test_authenticate(self, m):
        t = self.control._get_token_from_cache(
            "prolog")['token']
        u = fakes.create_usercrentials()['user_credentials']
        with mock.patch("bdocker.utils.read_yaml_file",
                        return_value=self.token_store):
            with mock.patch("bdocker.utils.write_yaml_file"):

                token = self.control.authenticate(admin_token=t,
                                                  session_data=u)
        self.assertIsNotNone(token)
        token_info = self.control._get_token_from_cache(token)
        self.assertEqual(u['uid'], token_info['uid'])
        self.assertEqual(u['home'], token_info['home'])
        self.assertEqual(u['gid'], token_info['gid'])
        self.assertNotIn('job', token_info)

    @mock.patch('bdocker.utils.check_user_credentials')
    def test_authenticate_with_job(self, m):
        jobid = uuid.uuid4().hex
        spool = uuid.uuid4().hex
        t = self.control._get_token_from_cache(
            "prolog")['token']
        u = fakes.create_usercrentials()['user_credentials']
        u.update({'job': {'job_id': jobid,
                          'spool': spool}
                  })
        with mock.patch("bdocker.utils.read_yaml_file",
                        return_value=self.token_store):
            with mock.patch("bdocker.utils.write_yaml_file"):
                token = self.control.authenticate(admin_token=t,
                                                  session_data=u)
        self.assertIsNotNone(token)
        job_info = self.control.get_job_from_token(token)
        self.assertEqual(jobid, job_info['job_id'])
        self.assertEqual(spool, job_info['spool'])
        self.assertNotIn('cgroup', job_info)

    @mock.patch('bdocker.utils.check_user_credentials')
    def test_authenticate_with_job_batch_info(self, m):
        jobid = uuid.uuid4().hex
        spool = uuid.uuid4().hex
        cgroup = uuid.uuid4().hex
        batch_info = {"cgroup": cgroup}
        t = self.control._get_token_from_cache(
            "prolog")['token']
        u = fakes.create_usercrentials()['user_credentials']
        u.update({'job': {'job_id': jobid,
                          'spool': spool}
                  })
        with mock.patch("bdocker.utils.read_yaml_file",
                        return_value=self.token_store) as m_r:
            with mock.patch("bdocker.utils.write_yaml_file"
                            )as m_w:

                token = self.control.authenticate(admin_token=t,
                                                  session_data=u)
                self.assertIsNotNone(token)
                self.control.set_token_batch_info(token,
                                                  batch_info)
                job_info = self.control.get_job_from_token(token)
                self.assertEqual(jobid, job_info['job_id'])
                self.assertEqual(spool, job_info['spool'])
                self.assertEqual(cgroup, job_info['cgroup'])
                self.assertEqual(True, m_r.called)
                self.assertEqual(True, m_w.called)

    def test_authorize(self):
        t = fakes.user_token
        ath = self.control.authorize(t)
        self.assertIsNotNone(ath)
        self.assertIsNotNone(ath['uid'])
        self.assertIsNotNone(ath['home'])
        self.assertIsNotNone(ath['gid'])
        self.assertIsNotNone(ath['containers'])
        self.assertIsNotNone(ath['job'])

    def test_authorize_err(self):
        t = 'tokenerr'
        self.assertRaises(
            exceptions.UserCredentialsException,
            self.control.authorize, t)

    def test_authorize_containers(self):
        t = fakes.user_token
        c = fakes.containers[0]
        ath = self.control.authorize_container(
            token=t,
            container_id=c)
        self.assertIs(c, ath)

    def test_authorize_container_err(self):
        t = fakes.user_token
        c = 'containererr'
        self.assertRaises(exceptions.UserCredentialsException,
                          self.control.authorize_container, t, c)

    def test_add_container(self):
        token = fakes.user_token
        c_id = uuid.uuid4().hex
        token_info = self.control._get_token_from_cache(token)
        self.assertIsNotNone(token_info['containers'])
        self.assertEqual(2,
                         token_info['containers'].__len__())
        with mock.patch("bdocker.utils.read_yaml_file",
                        return_value=self.token_store):
            with mock.patch("bdocker.utils.write_yaml_file"):
                self.control.add_container(token, c_id)
                self.assertIsNotNone(
                    token_info['containers'])
                self.assertEqual(3,
                                 token_info['containers'].__len__())

    def test_remove_container(self):
        token = fakes.user_token_no_container
        c_id = uuid.uuid4().hex
        token_info = self.control._get_token_from_cache(token)
        self.assertNotIn('containers', token_info)
        with mock.patch("bdocker.utils.read_yaml_file",
                        return_value=self.token_store):
            with mock.patch("bdocker.utils.write_yaml_file"):
                self.control.add_container(token, c_id)
                self.assertIsNotNone(token_info['containers'])
                self.assertEqual(1,
                                 token_info['containers'].__len__())
                self.control.remove_container(token, c_id)
                self.assertNotIn('containers', token_info)

    def test_authorize_images(self):
        t = fakes.user_token_no_container
        c = fakes.images[0]
        ath = self.control.authorize_image(
            token=t,
            image_id=c)
        self.assertIs(True, ath)

    def test_authorize_image_err(self):
        t = fakes.user_token
        c = '84848'
        self.assertRaises(exceptions.UserCredentialsException,
                          self.control.authorize_image, t, c)

    def test_add_image(self):
        token = fakes.user_token_no_images
        image_id = "image2"
        token_info = self.control._get_token_from_cache(token)
        self.assertNotIn('images', token_info)
        with mock.patch("bdocker.utils.read_yaml_file",
                        return_value=self.token_store):
            with mock.patch("bdocker.utils.write_yaml_file"):
                self.control.add_image(token, image_id)
                self.assertIsNotNone(
                    token_info['images'])
                self.assertEqual(1,
                                 token_info['images'].__len__())

    def test_remove_image(self):
        token = fakes.user_token
        c_id = fakes.images[0]
        token_info = self.control._get_token_from_cache(token)
        self.assertIn('images', token_info)
        self.assertEqual(1,
                         token_info['images'].__len__())
        with mock.patch("bdocker.utils.read_yaml_file",
                        return_value=self.token_store):
            with mock.patch("bdocker.utils.write_yaml_file"):
                self.control.remove_image(token, c_id)
                self.assertNotIn('images', token_info)

    def test_list_containers(self):
        t = fakes.user_token
        list_containers = self.control.list_containers(
            token=t)
        self.assertIsNotNone(list_containers)
        self.assertEqual(fakes.containers,
                         list_containers)

    def test_authorize_admin(self):
        t = fakes.admin_token
        out = self.control.authorize_admin(t)
        self.assertEqual(True, out)

    def test_authorize_admin_err(self):
        t = "err"
        self.assertRaises(exceptions.UserCredentialsException,
                          self.control.authorize_admin,
                          t
                          )

    @mock.patch.object(credentials.TokenController,
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

    @mock.patch.object(credentials.TokenController,
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
        token = fakes.user_token
        token_info = self.control._get_token_from_cache(token)
        home = uuid.uuid4().hex
        token_info["home"] = home
        with mock.patch("bdocker.utils.read_yaml_file",
                        return_value=self.token_store) as m_r:
            with mock.patch("bdocker.utils.write_yaml_file"
                            )as m_w:
                self.control._update_token(token, token_info)
                self.assertEqual(True, m_r.called)
                self.assertEqual(True, m_w.called)
                token_up = self.control._get_token_from_cache(
                    token
                )
                self.assertEqual(home, token_up["home"])

    def test_set_token(self):
        jobid = uuid.uuid4().hex
        spool = uuid.uuid4().hex
        cgroup = uuid.uuid4().hex
        gid = uuid.uuid4().hex
        uid = uuid.uuid4().hex
        home = uuid.uuid4().hex
        token_info = {"home": home,
                      "uid": uid,
                      "gid": gid,
                      "job": {
                          "job_id": jobid,
                          "cgroup": cgroup,
                          "spool": spool}
                      }
        with mock.patch("bdocker.utils.read_yaml_file",
                        return_value=self.token_store) as m_r:
            with mock.patch("bdocker.utils.write_yaml_file"
                            )as m_w:
                token = self.control._set_token(token_info)
                self.assertEqual(True, m_r.called)
                self.assertEqual(True, m_w.called)
                token_up = self.control._get_token_from_cache(
                    token
                )
                self.assertEqual(home, token_up["home"])

    def test_get_token(self):
        t = fakes.user_token
        expected = fakes.token_store[t]
        t_info = self.control.get_token(t)
        self.assertEqual(expected, t_info)

    def test_get_admin(self):
        expected = fakes.admin_token
        t_info = self.control.get_admin_token()
        self.assertEqual(expected, t_info)

    @mock.patch.object(credentials.TokenController, "_get_token_from_cache")
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

    @mock.patch.object(credentials.TokenController, "_get_token_from_cache")
    def test_get_job_from_token_err(self, m_gt):
        m_gt.side_effect = exceptions.UserCredentialsException("")
        self.assertRaises(exceptions.UserCredentialsException,
                          self.control.get_job_from_token,
                          None)

    @mock.patch.object(credentials.TokenController, "_update_token")
    @mock.patch.object(credentials.TokenController, "_get_token_from_cache")
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
