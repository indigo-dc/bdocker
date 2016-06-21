# -*- coding: utf-8 -*-

# Copyright 2016 LIP - INDIGO-DataCloud
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
import logging
import os
import time

from bdocker.common import cgroups_utils
from bdocker.common import exceptions
from bdocker.common import request
from bdocker.common import utils

LOG = logging.getLogger(__name__)


class BatchMasterController(object):
    def __init__(self, conf):
        pass


class SGEAccountingController(BatchMasterController):

    def __init__(self, conf):
        super(SGEAccountingController, self).__init__(conf=conf)
        if 'bdocker_accounting' in conf:
            self.bdocker_accounting = conf["bdocker_accounting"]
        else:
            self.bdocker_accounting = "/etc/bdocker_accounting"
            LOG.exception("bdocker_accounting parameter is not defined."
                          " Using %s by default. " %
                          self.bdocker_accounting)

        if 'sge_accounting' in conf:
            self.sge_accounting = conf["sge_accounting"]
        else:
            self.sge_accounting = "/opt/sge/default/common/accounting"
            LOG.exception("sge_accounting parameter is not defined."
                          " Using %s by default. " %
                          self.bdocker_accounting)

    def _get_sge_job_accounting(self, queue_name, host_name, job_id):
        any_word = "[^:]+"
        job_string = "%s:%s:%s:%s:%s:%s:" % (
            queue_name, host_name, any_word,
            any_word, any_word,job_id
        )
        job = utils.find_line(self.sge_accounting, job_string)
        return job.split(":")

    def _update_sge_accounting(self, string_list):
        job_string = ":".join(string_list)
        utils.add_to_file(self.bdocker_accounting, job_string)

    def set_job_accounting(self, accounting):
        try:
            utils.add_to_file(self.bdocker_accounting, accounting)
            return []
        except KeyError as e:
            raise exceptions.BatchException(message=None, e=e)
        raise exceptions.NoImplementedException("Needs to be implemented"
                                                "--set_job_accounting()--")


class BatchWNController(object):

    def __init__(self, conf, accounting_conf):
        self.conf = conf
        self.enable_cgroups = conf.get("enable_cgroups",
                                       False)
        self.root_cgroup = conf.get("cgroups_dir",
                                    "/sys/fs/cgroup")
        self.parent_group = conf.get("parent_cgroup", '/')
        try:
            # TODO(jorgesece): host should have http or https
            endpoint = 'http://%s:%s' % (
                accounting_conf['host'],
                accounting_conf['port']
            )
            self.request_control = request.RequestController(
                endopoint=endpoint
            )
        except Exception as e:
            raise exceptions.ConfigurationException("Accounting"
                                                    " server configuration failed"
                                                    )

    def get_job_info(self):
        raise exceptions.NoImplementedException("Get job information"
                                       "method")

    def conf_environment(self, job_id, spool_dir):
        if self.enable_cgroups:
            parent_pid = utils.read_file("%s/pid" % spool_dir)
            cgroups_utils.create_tree_cgroups(job_id,
                                self.parent_group,
                                root_parent=self.root_cgroup,
                                pid=parent_pid)
            if self.parent_group == "/":
                cgroup_job = "/%s" % job_id
            else:
                cgroup_job = "%s/%s" % (self.parent_group, job_id)
            # print "father %s" % os.getpid()
            # self._launch_job_control(os.getpid(), cgroup_job)
            # print "father? %s" % os.getpid()
            # open("/home/jorge/Daemon_Parent.log", "w").write("AQUI" + "\n")
            batch_info = {"cgroup": cgroup_job}
            LOG.debug("CGROUP CONTROL ACTIVATED ON: %s "
                      "JOB CGROUP: %s "
                     % (self.parent_group, cgroup_job))
        else:
            LOG.debug("CGROUP CONTROL NOT ACTIVATED")
            batch_info = None
        return batch_info

    def _launch_job_control(self, job_id, cgroup, cuotas=None):
        # todo(jorgesece): protect the file accounting for several access
        retCode = job_id
        try:
            pid = os.fork()
            if pid > 0:
                # Exit parent process
                return 0
        except OSError, e:
            raise exceptions.BatchException("fork failed: %d (%s)" % (e.errno, e.strerror))
            os.exit(1)
        os.setsid()
        while(true):
            time.sleep(10)
            acc = cgroups_utils.get_accounting(
                job_id,
                self.parent_group,
                root_parent=self.root_cgroup)
            # TODO(jorgesece): storage accounting

        os._exit(0)

    def clean_environment(self, job_id):
        if self.enable_cgroups:
            cgroups_utils.delete_tree_cgroups(job_id,
                                self.parent_group,
                                root_parent=self.root_cgroup)

    def get_accounting(self, job_id):
        if self.enable_cgroups:
            accounting = cgroups_utils.get_accounting(
                job_id,
                self.parent_group,
                root_parent=self.root_cgroup
            )
            return accounting
        raise exceptions.NoImplementedException(
            message="Still not supported")

    def notify_accounting(self, admin_token, host_name, job_id):
        raise exceptions.NoImplementedException(
                message="Still not supported")


class SGEController(BatchWNController):

    def __init__(self, *args, **kwargs):
        super(SGEController, self).__init__(*args, **kwargs)
        self.bdocker_accounting = self.conf.get("bdokcer_accounting",
                                                "/etc/bdocker_accounting")
        self.sge_accounting = self.conf.get("sge_accounting",
                                            "/opt/sge/default/common/accounting")

    def create_accounting(self, job):

        # acc = self.get_accounting(job_id)
        job_id = job['id']
        qname = job['queue_name']
        hostname = job['host_name']
        logname = job['log_name_name']
        job_name = job['job_name_name']
        account = job['account_name']
        cpu_usage = job.get('cpu_usage', None)  # position 37
        memory_usage = job.get('memory_usage', None)  # position 38
        io_usage = job.get('io_usage', "0")  # position 39
        priority = '0'
        group = "0"  # we do not need it for bdocker
        submission_time = '0'  # position 9
        start_time = "0"  # position 10
        end_time = '0'  # position 11
        failed = "0"  # position 12. Set 37 in case we kill it
        status = "0"  # pos 13. 0 for ok, 137 time end
        ru_wallclock = "0"  # end_time - start_time  # pos 14

        full_string = ("%s:%s:%s:%s:%s:%s:%s:%s:%s:%s:%s:%s:%s:%s"
                       ":0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0"
                       ":%s:%s:%s"
                       ":0:0:0:0:0:0" %
                       (qname, hostname, group, logname, job_name,
                        job_id, account, priority,
                        submission_time, start_time, end_time,
                        failed, status,
                        ru_wallclock, cpu_usage, memory_usage, io_usage))

        return full_string

    def notify_accounting(self, admin_token, job_info):
        if self.enable_cgroups:
            acc = self.create_accounting(job_info)
            path = "/set_accounting"
            parameters = {'admin_token': admin_token,
                          'accounting': acc}
            results = self.request_control.execute_post(
                path=path, parameters=parameters
            )
            return results
        else:
            raise exceptions.NoImplementedException(
                message="Still not supported")

    def get_job_info(self):
        job_id = os.getenv(
            'JOB_ID', None)
        home = os.path.realpath(os.getenv(
            'HOME', None))
        user = os.getenv(
            'USER', None)
        spool_dir = os.getenv(
            "SGE_JOB_SPOOL_DIR", None)
        qname = os.getenv(
            'QUEUE', None)
        hostname = os.getenv(
            'HOSTNAME', None)  # only available in prolog
        logname = os.getenv(
            'SGE_O_LOGNAME', None)
        job_name = os.getenv(
            'JOB_NAME', None)
        account = os.getenv(
            'SGE_ACCOUNT', None)
        return {'home': home,
                'id': job_id,
                'user_name': user,
                'spool': spool_dir,
                'queue_name': qname,
                'host_name': hostname,
                'log_name': logname,
                'job_name': job_name,
                'account_name': account
                }

