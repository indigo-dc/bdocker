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
from bdocker.common import utils

LOG = logging.getLogger(__name__)


class BatchController(object):

    def __init__(self, conf):
        self.enable_cgroups = conf.get("enable_cgroups",
                                       False)
        self.root_cgroup = conf.get("cgroups_dir",
                                    "/sys/fs/cgroup")
        self.parent_group = conf.get("parent_cgroup", '/')

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
            print "father %s" % os.getpid()
            self._launch_job_control(os.getpid(), cgroup_job)
            print "father? %s" % os.getpid()
            open("/home/jorge/Daemon_Parent.log", "w").write("AQUI" + "\n")
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

        # Configure the child processes environment
        #os.chdir("/")
        os.setsid()
        #os.umask(0)
        print "child %s" % os.getpid()
        print "sleeping..."
        time.sleep(10)
        print "...waking up"
        os._exit(0)

    def clean_environment(self, job_id):
        if self.enable_cgroups:
            cgroups_utils.delete_tree_cgroups(job_id,
                                self.parent_group,
                                root_parent=self.root_cgroup,)

    def check_accounting(self):
        return "retrieving job info"

    def write_accounting(self):
        return "writing account"


class SGEController(BatchController):

    def __init__(self, conf):
        super(SGEController, self).__init__(conf=conf)
        self.accounting_file = conf.get("accounting_file")

    def get_job_info(self):
        job_id = os.getenv(
            'JOB_ID', None)
        home = os.path.realpath(os.getenv(
            'HOME', None))
        user = os.getenv(
            'USER', None)
        spool_dir = os.getenv(
            "SGE_JOB_SPOOL_DIR", None)
        return {'home': home,
                'job_id': job_id,
                'user': user,
                'spool': spool_dir
                }

    def check_accounting(self, job_id, job_batch_info):
        raise exceptions.NoImplementedException(message="Still not supported")

    def _update_accounting(self, job_id, cpu, end_time=None,
                           failed=None, status=None, memory=None,
                           io_data=None):
        # todo(jorgesece): read char from job_id
        full_string = utils.read_file(self.accounting_file)
        string_splitted = full_string.split(":")
        start_time = string_splitted[9]
        if failed:   # position 12
            string_splitted[11] = failed

        if status:   # position 13
            string_splitted[12] = status

        if end_time:
            string_splitted[10] = end_time  # position 11
            ru_wallclock = end_time - start_time  # POS 14
            string_splitted[13] = ru_wallclock

        if cpu:   # position 37
            string_splitted[36] = cpu

        if memory:   # position 38
            string_splitted[37] = memory

        if io_data:   # position 39
            string_splitted[38] = io_data
        # todo(jorgesece): write the line in file

    def create_accounting(self):
        # Create in prolog

        # docker:ge-wn03.novalocal:hpc:jorgesece:bdocker_job.sh.o80:81:sge:15:1465486337:
        # 1465486332:1465486332:0:127:0:0.053201:0.100611:5632.000000:0:0:0:0:25024:0:0:0.000000:
        # 72:0:0:0:242:55:NONE:sysusers:NONE:1:0:0.000000:0.000000:0.000000:-U sysusers:0.000000:
        # NONE:0.000000:0:0
        qname = os.getenv(
            'QUEUE')
        hostname = os.getenv(
            'HOSTNAME')  # only available in prolog
        group = "0"  # we do not need it for bdocker
        logname = os.getenv(
            'SGE_O_LOGNAME')
        job_name = os.getenv(
            'JOB_NAME')
        job_id = os.getenv(
            'JOB_ID')
        account = os.getenv(
            'SGE_ACCOUNT')
        priority = '0'
        submission_time = '0'  # position 9
        start_time = int(time.time())  # position 10
        end_time = 'get time end from epoch'  # position 11
        failed = "0"  # position 12. Set 37 in case we kill it
        status = "get status"  # pos 13. 0 for ok, 137 time end
        ru_wallclock = end_time - start_time  # pos 14
        cpu = "get from cgproups" # position 37
        memory = "0" # position 38
        io = "0" # position 39

        full_string = ("%s:%s:%s:%s:%s:%s:%s:%s:%s:%s:%s:%s:%s:%s"
                       ":0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0"
                       ":%s:%s:%s"
                       ":0:0:0:0:0:0" %
                       (qname, hostname, group, logname, job_name, job_id, account, priority,
                        submission_time, start_time, end_time, failed, status,
                        ru_wallclock, cpu, memory, io))

        utils.add_to_file(self.accounting_file, full_string)
