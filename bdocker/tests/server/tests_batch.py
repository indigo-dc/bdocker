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

import io
import mock
import os
import testtools
import uuid

from bdocker.common.modules import batch
from bdocker.common import exceptions
from bdocker.common import request


class TestSGEAccController(testtools.TestCase):
    """Test ACCOUNTING SGE Batch controller."""
    def setUp(self):
        super(TestSGEAccController, self).setUp()
        conf = {"bdocker_accounting": "/foo",
        "sge_accounting": "/baa",
        }
        self.controller = batch.SGEAccountingController(conf)

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

    @mock.patch("__builtin__.open")
    def test_get_sge_job_accounting(self, mock_open):
        line = ("docker:ge-wn03.novalocal:hpc:jorgesece:bdocker_job.sh.o80:81:sge:15:1465486337:"
                "1465486332:1465486332:0:127:0:0.053201:0.100611:5632.000000:0:0:0:0:25024:0:0:0.000000:"
                "72:0:0:0:242:55:NONE:sysusers:NONE:1:0:0.000000:0.000000:0.000000:-U sysusers:0.000000:"
                "NONE:0.000000:0:0"
                )
        m_class = mock.MagicMock()
        m_class.readline.return_value = line
        mock_open.return_value = m_class
        queue = "docker"
        host_name= "ge-wn03.novalocal"
        job_id = "81"
        out = self.controller._get_sge_job_accounting(queue, host_name, job_id)
        expected = line.split(":")
        self.assertEqual(expected, out)

    @mock.patch("bdocker.common.utils.add_to_file")
    def test_update_accounting(self, m):
        controller = batch.SGEAccountingController(mock.MagicMock())
        out = controller.set_job_accounting(None)
        self.assertEqual([], out)


class TestSGEController(testtools.TestCase):
    """Test SGE Batch controller."""
    def setUp(self):
        super(TestSGEController, self).setUp()
        self.parent_path = "/systemd/user/"
        self.acc_conf = {"host": "/foo",
                         "port": "11"}

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
        controller = batch.SGEController(conf, self.acc_conf)
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
        controller = batch.SGEController(conf, self.acc_conf)
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
        controller = batch.SGEController(conf, self.acc_conf)
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
        controller = batch.SGEController(conf, self.acc_conf)
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
        controller = batch.SGEController(conf, self.acc_conf)
        controller.clean_environment(job_id)
        self.assertIs(False, m_del.called)

    @mock.patch("os.getenv")
    def test_get_job_info(self, m):
        job_id = uuid.uuid4().hex
        user = uuid.uuid4().hex
        home = "/home/rrr"
        spool_dir = "/foo"
        queue_name = "docker"
        host_name = "ge-wn03.novalocal"
        log_name = "jorgesece"
        job_name = "test.sh01"
        account = "sge"
        m.side_effect = [
            job_id,
            home,
            user,
            spool_dir,
            queue_name,
            host_name,
            log_name,
            job_name,
            account
        ]
        expected = {'home': home,
                    'id': job_id,
                    'queue_name': queue_name,
                    'host_name': host_name,
                    'log_name': log_name,
                    'job_name': job_name,
                    'account_name': account,
                    'spool': spool_dir,
                    'user_name': user
                    }
        out = batch.SGEController({}, self.acc_conf).get_job_info()
        self.assertEqual(expected, out)

    @mock.patch.object(request.RequestController, "execute_post")
    @mock.patch.object(batch.SGEController, "create_accounting")
    def test_notify_accounting(self, m_acc, m_post):
        job_id = uuid.uuid4().hex
        admin_token = uuid.uuid4().hex
        memory_usage = "1000"
        accounting = "/foo"
        m_acc.return_value = accounting
        job = {"field1": memory_usage,
               "id": job_id}
        conf = {"cgroups_dir": "/foo",
                "enable_cgroups": True,
                "parent_cgroup": "/bdocker.test"}
        controller = batch.SGEController(conf, self.acc_conf)
        controller.notify_accounting(admin_token,
                                     job)
        self.assertIs(True, m_post.called)
        m_post.assert_called_with(
            path="/set_accounting",
            parameters={"admin_token": admin_token,
                        "accounting": accounting
                        }
        )

    def test_notify_accounting_nocgroup(self):
        conf = {
                "enable_cgroups": False,
                }
        controller = batch.SGEController(conf, self.acc_conf)
        self.assertRaises(exceptions.NoImplementedException,
                          controller.notify_accounting,
                          None,
                          None)

    @mock.patch("os.getenv")
    def test_create_accounting(self, m):
        queue_name = "docker"
        host_name = "ge-wn03.novalocal"
        log_name = "jorgesece"
        job_id = "81"
        job_name = "test.sh01"
        account = "sge"
        cpu_usage = "33"
        memory_usage = "1000"
        io_usage = "0.00"
        expected = ("%s:%s:0:%s:%s:%s:%s:0:0:"
                "0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:"
                "0:0:0:0:0:0:0:0:0:0:0:%s:%s:%s:0:0:"
                "0:0:0:0"
                % (queue_name, host_name, log_name, job_name, job_id, account,
                   cpu_usage, memory_usage, io_usage)
                )
        controller = batch.SGEController({}, self.acc_conf)
        m.side_effect = [queue_name,
                         host_name,
                         log_name,
                         job_name,
                         job_id,
                         account
                         ]
        job = {'id': job_id,
               'queue_name': queue_name,
               'host_name': host_name,
               'log_name_name': log_name,
               'job_name_name': job_name,
               'account_name': account,
               'cpu_usage': cpu_usage,
               'memory_usage': memory_usage,
               'io_usage': io_usage
               }
        out = controller.create_accounting(job)

        self.assertEqual(expected, out)