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
import signal
import time

from bdocker import utils, exceptions
from bdocker.modules import cgroups_utils
from bdocker.modules import request

LOG = logging.getLogger(__name__)


class BatchNotificationController(object):
    def __init__(self, accounting_conf):
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
            raise exceptions.ConfigurationException(
                "Accounting"
                " server configuration failed %s. "
                % e.message
            )

    def notify_accounting(self, admin_token, accounting_info):
        path = "/set_accounting"

        parameters = {"admin_token": admin_token,
                      'accounting': accounting_info
                      }
        out = self.request_control.execute_put(
            path=path, parameters=parameters
        )
        LOG.exception("return from rq")
        return out


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
                          self.sge_accounting)

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
            LOG.exception("WRITING in %s" % self.bdocker_accounting)
            accounting_end_line = "%s\n" % accounting
            utils.add_to_file(self.bdocker_accounting, accounting_end_line)
            return []
        except BaseException as e:
            message = "ERROR UPDATING ACCOUNTING: %s. " % e.message
            LOG.exception(message)
            raise exceptions.BatchException(message=message)
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
        self.default_acc_file = ".bdocker_accounting"

        self.notification_controller = BatchNotificationController(accounting_conf)

    def conf_environment(self, session_data):
        if self.enable_cgroups:
            try:
                job_id = session_data['job']['id']
                job_spool = session_data['job']['spool']
            except KeyError as e:
                message = ("Job information error %s"
                           % e.message)
                raise exceptions.ParseException(message=message)
            parent_pid = utils.read_file("%s/pid" % job_spool)
            cgroups_utils.create_tree_cgroups(job_id,
                                self.parent_group,
                                root_parent=self.root_cgroup,
                                pid=parent_pid)
            if self.parent_group == "/":
                cgroup_job = "/%s" % job_id
            else:
                cgroup_job = "%s/%s" % (self.parent_group, job_id)
            batch_info = {"cgroup": cgroup_job}
            LOG.debug("CGROUP CONTROL ACTIVATED ON: %s "
                      "JOB CGROUP: %s "
                     % (self.parent_group, cgroup_job))
        else:
            LOG.exception("CGROUP CONTROL NOT ACTIVATED")
            batch_info = None
        return batch_info

    def clean_environment(self, session_data):
        if self.enable_cgroups:
            flag = True
            job_id = session_data["job"]["id"]
            cgroups_utils.delete_tree_cgroups(job_id,
                                self.parent_group,
                                root_parent=self.root_cgroup)
        else:
            LOG.exception("CGROUP CONTROL NOT ACTIVATED")
            flag = False
        return flag

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

    def create_accounting(self, job):
        raise exceptions.NoImplementedException(
                message="Still not supported")

    def notify_accounting(self, admin_token, host_name, job_id):
        raise exceptions.NoImplementedException(
                message="Still not supported")

    def get_job_info(self):
        raise exceptions.NoImplementedException("Get job information"
                                       "method")


class SGEController(BatchWNController):

    def __init__(self, *args, **kwargs):
        super(SGEController, self).__init__(*args, **kwargs)

    @staticmethod
    def _create_accounting_file(path, job_info):
        data = {
            "job_id": job_info['job_id'],
            "user_name": job_info['user_name'],
            "queue_name": job_info['queue_name'],
            "host_name": job_info['host_name'],
            "job_name": job_info['job_name'],
            "log_name": job_info['log_name'],
            "account_name": job_info['account_name']
        }
        utils.write_yaml_file(path, data)

    @staticmethod
    def _read_accounting_file(path):
        return utils.read_yaml_file(path)

    def _launch_job_monitoring(self, job_id, file_path,
                               admin_token, cuotas=None):
        LOG.exception("LAUNCH MONITORING")
        try:
            pid = os.fork()
            if pid > 0:
                # Exit parent process
                return 0
            os.setsid()
        except OSError, e:
            raise exceptions.BatchException("fork failed: %d (%s)" % (
                e.errno, e.strerror))
            LOG.exception("CREATING JOB MONITOR PROCESS")
            os.exit(1)

        LOG.exception("MONITORING")
        while True:
            try:
                LOG.exception("SLEEP")
                time.sleep(10)
                acc = cgroups_utils.get_accounting(
                     job_id,
                     self.parent_group,
                     root_parent=self.root_cgroup)
                #acc = {"update": "testing"}
                utils.update_yaml_file(file_path, acc)
                LOG.exception("WORKING")
            except exceptions.CgroupException as e:
                LOG.exception("MONITORING FINISHED")
                break
            except BaseException as e:
                LOG.exception("ERROR IN: %s. %s." % (file_path, e.message))
                break
            except:
                LOG.exception("ERROR IN MONITORING")
        child = os.getpid()
        LOG.exception("EXIT FROM MONITORING. FORK: %s" % child)
        os.kill(child, signal.SIG_IGN)
        time.sleep(0.1)

    def conf_environment(self, session_data, admin_token):
        out = super(SGEController, self).conf_environment(session_data)
        if out:
            try:
                job_info = session_data['job']
                job_id = job_info['id']
                path = "%s/%s_%s" % (session_data['home'],
                                     self.default_acc_file,
                                     job_id)
                out.update({"acc_file": path})
                self._create_accounting_file(path, job_info)
                self._launch_job_monitoring(job_id, path, admin_token)
            except KeyError as e:
                message = ("Job information error %s"
                           % e.message)
                raise exceptions.ParseException(message=message)
        return out

    def clean_environment(self, session_data, admin_token):
        out = super(SGEController, self).clean_environment(session_data)
        if out:
            try:
                job_id = session_data["job"]["id"]
                path = "%s/%s_%s" % (session_data['home'],
                                     self.default_acc_file,
                                     job_id)
                self.notify_accounting(admin_token, path)
                utils.delete_file(path)
            except KeyError as e:
                message = ("Job information error %s"
                           % e.message)
                raise exceptions.ParseException(message=message)
            except BaseException as e:
                message = ("ACCOUNTING NOTIFICATION ERROR %s"
                           % e.message)
                raise exceptions.BatchException(message=message)

    def create_accounting(self, job):
        try:
            job_id = job['job_id']
            qname = job['queue_name']
            hostname = job['host_name']
            logname = job['log_name']
            job_name = job['job_name']
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
        except KeyError as e:
            raise exceptions.ParseException(
                "Job accountig file malformed: %s. " % e.message
            )

    def notify_accounting(self, admin_token, path):
        if self.enable_cgroups:
            job_info = utils.read_yaml_file(path)
            accounting = self.create_accounting(job_info)
            LOG.exception("CREATE ACCOUNTING STRING: %s" % accounting)
            results = self.notification_controller.notify_accounting(
                    admin_token,
                    accounting)
            LOG.exception("NOTIFIED")
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
                'job_id': job_id,
                'user_name': user,
                'spool': spool_dir,
                'queue_name': qname,
                'host_name': hostname,
                'log_name': logname,
                'job_name': job_name,
                'account_name': account
                }

