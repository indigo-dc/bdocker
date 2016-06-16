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

import mock
import os
import testtools
import uuid

from bdocker.common.modules import batch
from bdocker.common import exceptions


class TestSGEAccController(testtools.TestCase):
    """Test ACCOUNTING SGE Batch controller."""
    def setUp(self):
        super(TestSGEAccController, self).setUp()

    def test_accounting_configuration(self):
        conf = {"bdocker_accounting": "/foo",
                "sge_accounting": "/baa",
                }
        controller = batch.SGEAccountingController(conf)
        self.assertEqual(conf["bdocker_accounting"], controller.bdocker_accounting)
        self.assertEqual(conf["sge_accounting"], controller.sge_accounting)

    def test_default_accounting_configuration(self):
        bdocker_accounting = "/etc/bdocker_accounting"
        sge_accounting = "/opt/sge/default/common/accounting"

        controller = batch.SGEAccountingController({})
        self.assertEqual(bdocker_accounting, controller.bdocker_accounting)
        self.assertEqual(sge_accounting, controller.sge_accounting)

    def test_update_accounting(self):
        conf = {"bdocker_accounting": "/foo",
                "sge_accounting": "/baa",
                }
        controller = batch.SGEAccountingController(conf)
        self.assertRaises(exceptions.NoImplementedException,
                          controller.update_accounting,
                          None, None, None,None)


class TestSGEController(testtools.TestCase):
    """Test SGE Batch controller."""
    def setUp(self):
        super(TestSGEController, self).setUp()
        self.parent_path = "/systemd/user/"

    @mock.patch("bdocker.common.utils.read_file")
    @mock.patch("bdocker.common.cgroups_utils.create_tree_cgroups")
    def test_conf_environment(self, m_cre, m_read):
        job_id = uuid.uuid4().hex
        spool_dir = "/foo"
        parent_id = uuid.uuid4().hex
        parent_dir = "/bdocker.test"
        conf = {"cgroups_dir": "/foo",
                "enable_cgroups": True,
                "parent_cgroup": parent_dir}
        m_read.return_value = parent_id
        controller = batch.SGEController(conf)
        batch_info = controller.conf_environment(job_id, spool_dir)
        expected_cgroup = {"cgroup": "%s/%s" % (parent_dir, job_id)}
        self.assertEqual(expected_cgroup, batch_info)
        self.assertIs(True, m_read.called)
        self.assertIs(True, m_cre.called)
        m_cre.assert_called_with(
            job_id,
            conf["parent_cgroup"],
            root_parent=conf["cgroups_dir"],
            pid=parent_id
        )

    @mock.patch("bdocker.common.utils.read_file")
    @mock.patch("bdocker.common.cgroups_utils.create_tree_cgroups")
    def test_conf_environment_no_root_dir(self, m_cre,  m_read):
        spool_dir = "/foo"
        job_id = uuid.uuid4().hex
        parent_id = uuid.uuid4().hex
        parent_dir = "/bdocker.test"
        conf = {
            "enable_cgroups": True,
            "parent_cgroup": parent_dir}
        m_read.return_value = parent_id
        controller = batch.SGEController(conf)
        batch_info = controller.conf_environment(job_id, spool_dir)
        expected_cgroup = {"cgroup": "%s/%s" % (parent_dir, job_id)}
        self.assertEqual(expected_cgroup, batch_info)
        self.assertIs(True, m_read.called)
        self.assertIs(True, m_cre.called)
        m_cre.assert_called_with(
            job_id,
            conf["parent_cgroup"],
            root_parent="/sys/fs/cgroup",
            pid=parent_id
        )

    @mock.patch("bdocker.common.utils.read_file")
    @mock.patch("bdocker.common.cgroups_utils.create_tree_cgroups")
    def test_conf_environment_no_cgroup(self, m_cre, m_read):
        spool_dir = "/foo"
        job_id = uuid.uuid4().hex
        parent_id = uuid.uuid4().hex
        conf = {"cgroups_dir": "/foo",
                "parent_cgroup": "/bdocker.test"}
        m_read.return_value = parent_id
        controller = batch.SGEController(conf)
        batch_info = controller.conf_environment(job_id, spool_dir)
        self.assertIsNone(batch_info)
        self.assertIs(False, m_read.called)
        self.assertIs(False, m_cre.called)

    @mock.patch("bdocker.common.cgroups_utils.delete_tree_cgroups")
    def test_clean_environment(self, m_del):
        job_id = uuid.uuid4().hex
        conf = {"cgroups_dir": "/foo",
                "enable_cgroups": True,
                "parent_cgroup": "/bdocker.test"}
        controller = batch.SGEController(conf)
        controller.clean_environment(job_id,)
        self.assertIs(True, m_del.called)
        m_del.assert_called_with(
            job_id,
            conf["parent_cgroup"],
            root_parent=conf["cgroups_dir"]
        )

    @mock.patch("bdocker.common.cgroups_utils.delete_tree_cgroups")
    def test_clean_environment_no_cgroup(self, m_del):
        job_id = uuid.uuid4().hex
        conf = {"cgroups_dir": "/foo",
                "parent_cgroup": "/bdocker.test"}
        controller = batch.SGEController(conf)
        controller.clean_environment(job_id)
        self.assertIs(False, m_del.called)

    def test_get_job_info(self):
        job_id = uuid.uuid4().hex
        user = uuid.uuid4().hex
        spool_dir = "/foo"
        os.environ["JOB_ID"] = job_id
        home = os.getenv("HOME")
        os.environ["USER"] = user
        os.environ["SGE_JOB_SPOOL_DIR"] = spool_dir
        expected = {'home': home,
                    'job_id': job_id,
                    'user': user,
                    'spool': spool_dir,
                    }
        out = batch.SGEController({}).get_job_info()
        self.assertEqual(out, expected)

