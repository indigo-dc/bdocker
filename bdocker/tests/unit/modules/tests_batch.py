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

from bdocker import exceptions
from bdocker.modules import batch
from bdocker.modules import request
from bdocker.tests import fakes


class TestBacthNotificationController(testtools.TestCase):

    def setUp(self):
        super(TestBacthNotificationController, self).setUp()
        self.acc_conf = {"host": "/foo",
                         "port": "11"}

    @mock.patch.object(request.RequestController, "execute_put")
    def test_notify_accounting(self, m_post):
        job_id = uuid.uuid4().hex
        admin_token = uuid.uuid4().hex
        memory_usage = "1000"
        accounting_info = {"field1": memory_usage,
                           "job_id": job_id}
        controller = batch.BatchNotificationController(
            self.acc_conf)
        controller.notify_accounting(
            admin_token, accounting_info)
        self.assertIs(True, m_post.called)
        m_post.assert_called_with(
            path="/set_accounting",
            parameters={"admin_token": admin_token,
                        "accounting": accounting_info
                        }
        )


class TestSGEAccController(testtools.TestCase):
    """Test ACCOUNTING SGE Batch controller."""
    def setUp(self):
        super(TestSGEAccController, self).setUp()

    def test_accounting_configuration(self):
        conf = {"bdocker_accounting": uuid.uuid4().hex}
        controller = batch.AccountingController(conf)
        self.assertEqual(conf["bdocker_accounting"],
                         controller.bdocker_accounting)

    def test_default_accounting_configuration(self):
        bdocker_accounting = "/etc/bdocker_accounting"
        conf = {}
        controller = batch.AccountingController(conf)
        self.assertEqual(bdocker_accounting,
                         controller.bdocker_accounting)

    @mock.patch("bdocker.utils.add_to_file")
    def test_update_accounting(self, m):
        controller = batch.SGEAccountingController(mock.MagicMock())
        out = controller.set_job_accounting(None)
        self.assertEqual([], out)


class TestWNController(testtools.TestCase):

    @mock.patch("os.fork")
    @mock.patch("os.setsid")
    @mock.patch("time.sleep")
    @mock.patch("bdocker.modules.cgroups_utils.get_accounting")
    @mock.patch.object(batch.CgroupsWNController, "create_accounting_file")
    @mock.patch("bdocker.utils.update_yaml_file")
    @mock.patch("os.getpid")
    @mock.patch("os.kill")
    def test_launch_job_monitoring_interval(self, m_kill,
                                            m_getpid, m_update,
                                            m_read,
                                            m_acc, m_sleep,
                                            m_setsid, m_fork):
        job_id = fakes.job_id
        job_info = fakes.job_info
        path = "/foo"
        memory_usage = 99
        cpu_usage = 111
        interval = 33
        acc = {"memory_usage": memory_usage,
               "cpu_usage": cpu_usage}
        conf = {"cgroups_dir": "/foo",
                "enable_cgroups": True,
                "parent_cgroup": "/bdocker.test",
                "flush_time": interval,
                "only_docker_accounting": False,
                "accounting_endpoint": mock.MagicMock()
                }
        m_fork.return_value = 0
        m_acc.return_value = acc
        controller = batch.CgroupsWNController(conf)
        m_update.side_effect = exceptions.CgroupException("Finished")
        controller.launch_job_monitoring(job_id,
                                         job_info,
                                         path,
                                         None, None, None)
        m_sleep.side_effect = [interval, 0.1]
        m_update.assert_called_with(
            path, acc)
        m_read.assert_called_with(path, job_info)

    @mock.patch("os.fork")
    @mock.patch("os.setsid")
    @mock.patch("time.sleep")
    @mock.patch("bdocker.modules.cgroups_utils.get_accounting")
    @mock.patch.object(batch.CgroupsWNController, "create_accounting_file")
    @mock.patch("bdocker.utils.update_yaml_file")
    @mock.patch("os.getpid")
    @mock.patch("os.kill")
    @mock.patch.object(batch.CgroupsWNController, "kill_job")
    def test_launch_job_monitoring(self, m_kill_job, m_kill,
                                   m_getpid, m_update, m_read,
                                   m_acc, m_sleep,
                                   m_setsid, m_fork):
        job_id = fakes.job_id
        job_info = fakes.job_info
        path = "/foo"
        memory_usage = 99
        cpu_usage = 111
        interval = 33
        acc = {"memory_usage": memory_usage,
               "cpu_usage": cpu_usage}
        conf = {"cgroups_dir": "/foo",
                "enable_cgroups": True,
                "parent_cgroup": "/bdocker.test",
                "flush_time": interval,
                "only_docker_accounting": False,
                "accounting_endpoint": mock.MagicMock()
                }

        m_fork.return_value = 0
        m_acc.return_value = acc
        controller = batch.CgroupsWNController(conf)
        m_update.side_effect = exceptions.CgroupException("Finished")
        controller.launch_job_monitoring(job_id, job_info,
                                         path,
                                         None, None, None)
        m_sleep.side_effect = [interval, 0.1]
        m_update.assert_called_with(
            path, acc)
        m_read.assert_called_with(path, job_info)

    @mock.patch("os.fork")
    @mock.patch("os.setsid")
    @mock.patch("time.sleep")
    @mock.patch("bdocker.modules.cgroups_utils.get_accounting")
    @mock.patch.object(batch.CgroupsWNController, "create_accounting_file")
    @mock.patch("bdocker.utils.update_yaml_file")
    @mock.patch("os.getpid")
    @mock.patch("os.kill")
    @mock.patch.object(batch.CgroupsWNController, "kill_job")
    def test_launch_job_monitoring_only_docker(self, m_kill_job, m_kill,
                                               m_getpid, m_update, m_read,
                                               m_acc, m_sleep,
                                               m_setsid, m_fork):
        job_id = fakes.job_id
        job_info = fakes.job_info
        path = "/foo"
        memory_usage = [99, 10]
        cpu_usage = [111, 10]
        interval = 33
        acc = [{"memory_usage": memory_usage[0],
                "cpu_usage": cpu_usage[0]},
               {"memory_usage": memory_usage[1],
                "cpu_usage": cpu_usage[1]}
               ]
        expectec_acc = {"memory_usage": memory_usage[0] - memory_usage[1],
                        "cpu_usage": cpu_usage[0] - cpu_usage[1]
                        }
        conf = {"cgroups_dir": "/foo",
                "enable_cgroups": True,
                "parent_cgroup": "/bdocker.test",
                "flush_time": interval,
                "only_docker_accounting": True,
                "accounting_endpoint": mock.MagicMock()
                }

        m_fork.return_value = 0
        m_acc.side_effect = [acc[0], acc[1]]
        controller = batch.CgroupsWNController(conf)
        m_update.side_effect = exceptions.CgroupException("Finished")
        controller.launch_job_monitoring(job_id, job_info,
                                         path,
                                         None, None, None)
        m_sleep.side_effect = [interval, 0.1]
        m_update.assert_called_with(
            path, expectec_acc)
        m_read.assert_called_with(path, job_info)

    @mock.patch("os.fork")
    @mock.patch("os.setsid")
    @mock.patch("time.sleep")
    @mock.patch("bdocker.modules.cgroups_utils.get_accounting")
    @mock.patch.object(batch.CgroupsWNController, "create_accounting_file")
    @mock.patch("bdocker.utils.update_yaml_file")
    @mock.patch("os.getpid")
    @mock.patch("os.kill")
    @mock.patch.object(batch.CgroupsWNController, "kill_job")
    def test_launch_job_monitoring_cuotas(self, m_kill_job,
                                          m_kill,
                                          m_getpid, m_update,
                                          m_read,
                                          m_acc, m_sleep,
                                          m_setsid, m_fork):
        job_id = fakes.job_id
        job_info = fakes.job_info
        path = "/foo"
        memory_usage = 99
        cpu_usage = 111
        interval = 33
        spool = "/baa"
        cpu_max = 1111
        mem_max = 999
        acc = {"memory_usage": memory_usage,
               "cpu_usage": cpu_usage}
        conf = {"cgroups_dir": "/foo",
                "enable_cgroups": True,
                "parent_cgroup": "/bdocker.test",
                "flush_time": interval,
                "only_docker_accounting": False,
                "accounting_endpoint": mock.MagicMock()
                }
        m_fork.return_value = 0
        m_acc.side_effect = [acc,
                             exceptions.CgroupException("Finished")]
        controller = batch.CgroupsWNController(conf)
        controller.launch_job_monitoring(job_id,
                                         job_info,
                                         path,
                                         spool, cpu_max, mem_max)
        m_sleep.side_effect = [interval, 0.1]
        m_update.assert_called_with(
            path, acc)
        self.assertEqual(False, m_kill_job.called)
        self.assertEqual(0, m_kill_job.call_count)
        m_read.assert_called_with(path, job_info)

    @mock.patch("os.fork")
    @mock.patch("os.setsid")
    @mock.patch("time.sleep")
    @mock.patch("bdocker.modules.cgroups_utils.get_accounting")
    @mock.patch.object(batch.CgroupsWNController, "create_accounting_file")
    @mock.patch("bdocker.utils.update_yaml_file")
    @mock.patch("os.getpid")
    @mock.patch("os.kill")
    @mock.patch.object(batch.CgroupsWNController, "kill_job")
    def test_launch_job_monitoring_cuotas_killed_cpu(self, m_kill_job,
                                                     m_kill, m_getpid,
                                                     m_update, m_read,
                                                     m_acc, m_sleep,
                                                     m_setsid, m_fork):
        job_id = fakes.job_id
        job_info = fakes.job_info
        path = "/foo"
        memory_usage = 99
        cpu_usage = 111
        interval = 33
        spool = "/baa"
        cpu_max = 11
        mem_max = 999
        acc = {"memory_usage": memory_usage,
               "cpu_usage": cpu_usage}
        conf = {"cgroups_dir": "/foo",
                "enable_cgroups": True,
                "parent_cgroup": "/bdocker.test",
                "flush_time": interval,
                "only_docker_accounting": False,
                "accounting_endpoint": mock.MagicMock()
                }
        m_fork.return_value = 0
        m_acc.side_effect = [acc,
                             exceptions.CgroupException("Finished")]
        controller = batch.CgroupsWNController(conf)

        controller.launch_job_monitoring(job_id,
                                         job_info,
                                         path,
                                         spool, cpu_max, mem_max)
        m_sleep.side_effect = [interval, 0.1]
        m_update.assert_called_with(
            path, acc)
        self.assertEqual(True, m_kill_job.called)
        self.assertEqual(1, m_kill_job.call_count)
        m_read.assert_called_with(path, job_info)

    @mock.patch("os.fork")
    @mock.patch("os.setsid")
    @mock.patch("time.sleep")
    @mock.patch("bdocker.modules.cgroups_utils.get_accounting")
    @mock.patch.object(batch.CgroupsWNController, "create_accounting_file")
    @mock.patch("bdocker.utils.update_yaml_file")
    @mock.patch("os.getpid")
    @mock.patch("os.kill")
    @mock.patch.object(batch.CgroupsWNController, "kill_job")
    def test_launch_job_monitoring_cuotas_killed_mem(self, m_kill_job,
                                                     m_kill, m_getpid,
                                                     m_update, m_read,
                                                     m_acc, m_sleep,
                                                     m_setsid, m_fork):
        job_id = fakes.job_id
        job_info = fakes.job_info
        path = "/foo"
        memory_usage = 99
        cpu_usage = 2  # nanoseconds
        interval = 33
        spool = "/baa"
        cpu_max = 40
        mem_max = 9
        acc = {"memory_usage": memory_usage,
               "cpu_usage": cpu_usage}
        conf = {"cgroups_dir": "/foo",
                "enable_cgroups": True,
                "parent_cgroup": "/bdocker.test",
                "flush_time": interval,
                "only_docker_accounting": False,
                "accounting_endpoint": mock.MagicMock()
                }
        m_fork.return_value = 0
        m_acc.side_effect = [acc,
                             exceptions.CgroupException("Finished")]
        controller = batch.CgroupsWNController(conf)

        controller.launch_job_monitoring(job_id,
                                         job_info,
                                         path,
                                         spool, cpu_max, mem_max)
        m_sleep.side_effect = [interval, 0.1]
        m_update.assert_called_with(
            path, acc)
        self.assertEqual(True, m_kill_job.called)
        self.assertEqual(1, m_kill_job.call_count)
        m_read.assert_called_with(path, job_info)


class TestSGEController(testtools.TestCase):
    """Test SGE Batch controller."""
    def setUp(self):
        super(TestSGEController, self).setUp()
        self.parent_path = "/systemd/user/"
        self.acc_conf = "http://xx:22"

    @mock.patch("bdocker.utils.write_yaml_file")
    def test_create_accounting_file(self, m):
        controller = batch.SGEWNController(mock.MagicMock())
        job_id = uuid.uuid4().hex
        username = "username"
        queue_name = "queue_name"
        host_name = "host_name"
        job_name = "job_name"
        log_name = "log_name"
        account_name = "account_name"
        submission_time = "submission_time"
        job = {"job_id": job_id,
               "user_name": username,
               "queue_name": queue_name,
               "host_name": host_name,
               "job_name": job_name,
               "log_name": log_name,
               "account_name": account_name,
               "submission_time": submission_time
               }

        controller.create_accounting_file(None, job)
        m.assert_called_with(
            None,
            job
        )

    @mock.patch("bdocker.modules.cgroups_utils.create_tree_cgroups")
    @mock.patch.object(batch.CgroupsWNController, "launch_job_monitoring")
    @mock.patch.object(batch.SGEWNController, "notify_accounting")
    def test_conf_environment(self, m_not, m_lan, m_cre):
        admin_token = fakes.admin_token
        home = "/aa"
        parent_dir = "/bdocker.test"
        conf = {"cgroups_dir": "/foo",
                "enable_cgroups": True,
                "parent_cgroup": parent_dir,
                "accounting_endpoint": self.acc_conf}

        controller = batch.SGEWNController(conf)
        job_info = {"home": home,
                    "job": fakes.job_info,
                    }
        batch_info = controller.conf_environment(job_info, admin_token)
        expected_cgroup = {
            "cgroup": "%s/%s" % (parent_dir, fakes.job_id),
            "acc_file": "%s/.bdocker_accounting_%s" % (home,
                                                       fakes.job_id)
        }
        self.assertEqual(expected_cgroup, batch_info)
        self.assertIs(True, m_cre.called)

        expected_dict_1 = {'root_parent': conf["cgroups_dir"],
                           'pid': None}
        expected_creation_1 = (fakes.job_id,
                               conf["parent_cgroup"]
                               )
        self.assertEqual(expected_creation_1,
                         m_cre.mock_calls[0][1])
        self.assertEqual(expected_dict_1,
                         m_cre.mock_calls[0][2])

        expected_dict_2 = {'root_parent': conf["cgroups_dir"],
                           'pid': fakes.parent_pid}
        expected_creation_2 = (batch.JOB_PROCESS_CGROUP,
                               "%s/%s" % (conf["parent_cgroup"], fakes.job_id)
                               )
        self.assertEqual(expected_creation_2,
                         m_cre.mock_calls[1][1])
        self.assertEqual(expected_dict_2,
                         m_cre.mock_calls[1][2])

    @mock.patch("bdocker.modules.cgroups_utils.create_tree_cgroups")
    @mock.patch.object(batch.SGEWNController, "launch_job_monitoring")
    @mock.patch.object(batch.SGEWNController, "notify_accounting")
    def test_conf_environment_no_root_dir(self, m_not, m_lan,
                                          m_cre):
        home = "/foo"
        admin_token = uuid.uuid4().hex
        parent_id = fakes.parent_pid
        parent_dir = "/bdocker.test"
        conf = {
            "enable_cgroups": True,
            "parent_cgroup": parent_dir,
            "accounting_endpoint": self.acc_conf}
        job_info = {"home": home,
                    "job": fakes.job_info,
                    }
        controller = batch.SGEWNController(conf)
        batch_info = controller.conf_environment(job_info, admin_token)
        expected_cgroup = {
            "cgroup": "%s/%s" % (parent_dir, fakes.job_id),
            "acc_file": "%s/.bdocker_accounting_%s" % (home, fakes.job_id)
        }
        self.assertEqual(expected_cgroup, batch_info)
        self.assertIs(True, m_cre.called)
        expected_dict_1 = {'root_parent': "/sys/fs/cgroup",
                           'pid': None}
        expected_creation_1 = (fakes.job_id,
                               conf["parent_cgroup"]
                               )
        self.assertEqual(expected_creation_1,
                         m_cre.mock_calls[0][1])
        self.assertEqual(expected_dict_1,
                         m_cre.mock_calls[0][2])

        expected_dict_2 = {'root_parent': "/sys/fs/cgroup",
                           'pid': parent_id}
        expected_creation_2 = (batch.JOB_PROCESS_CGROUP,
                               "%s/%s" % (conf["parent_cgroup"], fakes.job_id)
                               )
        self.assertEqual(expected_creation_2,
                         m_cre.mock_calls[1][1])
        self.assertEqual(expected_dict_2,
                         m_cre.mock_calls[1][2])

    @mock.patch("bdocker.utils.read_file")
    @mock.patch("bdocker.modules.cgroups_utils.create_tree_cgroups")
    def test_conf_environment_no_cgroup(self, m_cre, m_read):
        spool_dir = "/foo"
        home = "/foo"
        admin_token = uuid.uuid4().hex
        job_id = uuid.uuid4().hex
        parent_id = uuid.uuid4().hex
        m_read.return_value = parent_id
        job_info = {"home": home,
                    "job": {"job_id": job_id,
                            "spool": spool_dir
                            }
                    }
        conf = {"cgroups_dir": "/foo",
                "parent_cgroup": "/bdocker.test",
                "accounting_endpoint": self.acc_conf}
        controller = batch.SGEWNController(conf)
        batch_info = controller.conf_environment(job_info, admin_token)
        self.assertIsNone(batch_info)
        self.assertIs(False, m_read.called)
        self.assertIs(False, m_cre.called)

    @mock.patch("bdocker.modules.cgroups_utils.delete_tree_cgroups")
    @mock.patch("bdocker.utils.delete_file")
    @mock.patch.object(batch.SGEWNController, "notify_accounting")
    def test_clean_environment(self, m_not, m_del_file, m_del_tree):
        admin_token = uuid.uuid4().hex
        job_id = uuid.uuid4().hex
        home = "/foo"
        spool_dir = "/foo"
        job_info = {"home": home,
                    "job": {"job_id": job_id,
                            "spool": spool_dir
                            }
                    }
        conf = {"cgroups_dir": "/foo",
                "enable_cgroups": True,
                "parent_cgroup": "/bdocker.test",
                "accounting_endpoint": self.acc_conf}
        controller = batch.SGEWNController(conf)
        controller.clean_environment(job_info, admin_token)
        self.assertIs(True, m_del_file.called)
        self.assertIs(True, m_del_tree.called)
        m_del_tree.assert_called_with(
            job_id,
            conf["parent_cgroup"],
            root_parent=conf["cgroups_dir"]
        )

    @mock.patch("bdocker.modules.cgroups_utils.delete_tree_cgroups")
    @mock.patch("bdocker.utils.delete_file")
    def test_clean_environment_no_cgroup(self, m_del_file, m_del_tree):
        admin_token = uuid.uuid4().hex
        job_id = uuid.uuid4().hex
        home = "/foo"
        spool_dir = "/foo"
        job_info = {"home": home,
                    "job": {"job_id": job_id,
                            "spool": spool_dir
                            }
                    }
        conf = {"cgroups_dir": "/foo",
                "enable_cgroups": False,
                "parent_cgroup": "/bdocker.test",
                "accounting_endpoint": self.acc_conf}
        controller = batch.SGEWNController(conf)
        controller.clean_environment(job_info, admin_token)
        self.assertIs(False, m_del_tree.called)

    @mock.patch("os.getenv")
    @mock.patch.object(batch.SGEWNController, "_get_job_configuration")
    def test_get_job_info(self, m_conf, m_env):
        job_id = uuid.uuid4().hex
        user = uuid.uuid4().hex
        home = "/home/rrr"
        spool_dir = "/foo"
        queue_name = "docker"
        host_name = "ge-wn03.novalocal"
        log_name = "jorgesece"
        job_name = "test.sh01"
        account = "sge"
        max_cpu = 22
        max_memory = 33
        m_env.side_effect = [
            job_id,
            home,
            user,
            spool_dir
        ]
        m_conf.return_value = {
            'queue_name': queue_name,
            'host_name': host_name,
            'log_name': log_name,
            'job_name': job_name,
            'account_name': account,
            'max_cpu': max_cpu,
            'max_memory': max_memory,
            'parent_pid': fakes.parent_pid
        }
        expected = {'home': home,
                    'job_id': job_id,
                    'queue_name': queue_name,
                    'host_name': host_name,
                    'log_name': log_name,
                    'job_name': job_name,
                    'account_name': account,
                    'spool': spool_dir,
                    'user_name': user,
                    'max_cpu': max_cpu,
                    'max_memory': max_memory,
                    'parent_pid': fakes.parent_pid
                    }
        conf = mock.MagicMock()
        out = batch.SGEWNController(conf).get_job_info()
        self.assertEqual(expected, out)

    @mock.patch.object(batch.SGEWNController, "create_accounting_register")
    @mock.patch.object(batch.BatchNotificationController, "notify_accounting")
    def test_notify_accounting(self, m_ba_not, m_acc):
        job_id = uuid.uuid4().hex
        admin_token = uuid.uuid4().hex
        memory_usage = "1000"
        accounting = "/foo"
        m_acc.return_value = accounting
        job = {"field1": memory_usage,
               "job_id": job_id}
        conf = {"cgroups_dir": "/foo",
                "enable_cgroups": True,
                "parent_cgroup": "/bdocker.test",
                "accounting_endpoint": self.acc_conf}
        controller = batch.SGEWNController(conf)
        controller.notify_accounting(admin_token, job)
        self.assertIs(True, m_ba_not.called)

    def test_notify_accounting_nocgroup(self):
        conf = {"cgroups_dir": "/foo",
                "enable_cgroups": False,
                "parent_cgroup": "/bdocker.test",
                "accounting_endpoint": self.acc_conf}
        controller = batch.SGEWNController(conf)
        self.assertRaises(exceptions.NoImplementedException,
                          controller.notify_accounting,
                          None,
                          None)

    @mock.patch("os.getenv")
    @mock.patch("bdocker.utils.read_yaml_file")
    @mock.patch('time.time')
    def test_create_accounting(self, m_time, m_read, m):
        queue_name = "docker"
        host_name = "ge-wn03.novalocal"
        log_name = "jorgesece"
        job_id = uuid.uuid4().hex
        job_name = "test.sh01"
        account = "sge"
        cpu_usage = "33"
        submission_time = "33"
        start_time = "334433"
        end_time = "4444"
        m_time.return_value = end_time
        memory_usage = "1000"
        io_usage = "0.00"
        expected = ("%s:%s:0:%s:%s:%s:%s:0:%s:"
                    "%s:%s:0:0:0:0:0:0:0:0:0:0:0:0:0:0:"
                    "0:0:0:0:0:0:0:0:0:0:0:%s:%s:%s:0:0:"
                    "0:0:0:0"
                    % (queue_name, host_name, log_name,
                       job_name, job_id, account,
                       submission_time, start_time, end_time,
                       cpu_usage, memory_usage, io_usage)
                    )
        conf = {"cgroups_dir": "/foo",
                "enable_cgroups": True,
                "parent_cgroup": "/bdocker.test",
                "accounting_endpoint": self.acc_conf}
        controller = batch.SGEWNController(conf)
        m.side_effect = [queue_name,
                         host_name,
                         log_name,
                         job_name,
                         job_id,
                         account
                         ]
        m_read.return_value = {'job_id': job_id,
                               'queue_name': queue_name,
                               'host_name': host_name,
                               'log_name': log_name,
                               'job_name': job_name,
                               'account_name': account,
                               'cpu_usage': cpu_usage,
                               'memory_usage': memory_usage,
                               'io_usage': io_usage,
                               'submission_time': submission_time,
                               'start_time': start_time,
                               'end_time': end_time
                               }
        out = controller.create_accounting_register(None)
        self.assertEqual(expected, out)

    @mock.patch("bdocker.utils.read_file")
    @mock.patch("bdocker.parsers.parse_time_to_nanoseconds")
    @mock.patch("bdocker.utils.load_sge_job_configuration")
    def test_get_job_configuration(self, m_load, m_parse, m_read):
        queue = "ff"
        host = "ooo.nova"
        job_owner = "uyo"
        account = "accseg"
        max_cpu = "00:40:00"
        max_mem = 11
        job_name = "rrrr"
        submission_t = 999
        m_read.return_value = fakes.parent_pid
        m_load.return_value = {"queue": queue,
                               "host": host,
                               "job_owner": job_owner,
                               "job_name": job_name,
                               "account": account,
                               "h_cpu": max_cpu,
                               "h_data": max_mem,
                               "submission_time": submission_t,
                               "parent_pid": fakes.parent_pid,
                               "terminate_method": ""
                               }
        cpu_parsed = 100
        m_parse.return_value = cpu_parsed
        controller = batch.SGEWNController(mock.MagicMock())
        info = controller._get_job_configuration(None)
        self.assertEqual(queue, info["queue_name"])
        self.assertEqual(host, info["host_name"])
        self.assertEqual(job_owner, info["log_name"])
        self.assertEqual(job_name, info["job_name"])
        self.assertEqual(account, info["account_name"])
        self.assertEqual(cpu_parsed, info["max_cpu"])
        self.assertEqual(max_mem, info["max_memory"])
