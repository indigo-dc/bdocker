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

import abc
import os
import signal
import time

import six

from bdocker import exceptions
from bdocker.modules import cgroups_utils
from bdocker.modules import request
from bdocker import parsers
from bdocker import utils

BDOCKER_ACCOUNTING = "/etc/bdocker_accounting"
LOCAL_ACCOUNTING_FILE = ".bdocker_accounting"
JOB_PROCESS_CGROUP = 'COMMON'


class BatchNotificationController(object):
    """Notification controller for batch systems."""
    def __init__(self, accounting_endpoint):
        """Initialize the controller

        It set attributes and creates a Request controller by using
        the endpoint related to the accounting server.

        :param accounting_endpoint:
        :return:
        """
        try:
            self.request_control = request.RequestController(
                endopoint=accounting_endpoint
            )
        except Exception as e:
            raise exceptions.ConfigurationException(
                "Accounting"
                " server configuration failed %s. "
                % e.message
            )

    def notify_accounting(self, admin_token, accounting_info):
        """Execute a PUT request to notify the accounting

        In order to notify the job accounting information,
        it executes a PUT request to the accounting server

        :param admin_token: administration token.
        :param accounting_info: string within the accounting
         information
        :return: response output
        """
        path = "/set_accounting"

        parameters = {"admin_token": admin_token,
                      'accounting': accounting_info
                      }
        out = self.request_control.execute_put(
            path=path, parameters=parameters
        )
        exceptions.make_log("info", "ACCOUNTING DONE")
        return out


@six.add_metaclass(abc.ABCMeta)
class AccountingController(object):
    """Base of the Accounting the controller."""

    def __init__(self, conf):
        """Initialize controller

        :param conf: dictionary with the bdocker configuration
        :return:
        """
        if 'bdocker_accounting' in conf:
            self.bdocker_accounting = conf["bdocker_accounting"]
        else:
            self.bdocker_accounting = BDOCKER_ACCOUNTING
            exceptions.make_log("exception",
                                "bdocker_accounting parameter is not defined."
                                " Using %s by default. " %
                                self.bdocker_accounting)

    def set_job_accounting(self, accounting):
        """Add accounting line to the bdocker accounting file

        It is different for each batch scheduler, so, this class
        does not implement it.

        :param accounting: string with sge accounting format
        :return: empty array
        """
        pass


class SGEAccountingController(AccountingController):
    """SGE accounting controller."""
    def __init__(self, *args, **kwargs):
        """Initialize controller

        :param conf: dictionary with the bdocker configuration
        :return:
        """
        super(SGEAccountingController, self).__init__(*args, **kwargs)

    @staticmethod
    def _get_sge_job_accounting(queue_name, host_name, job_id):
        """Get information from the SGE accounting file.

        It is DEPRECATED. We keep it in case we need in the future.

        :param queue_name:
        :param host_name:
        :param job_id:
        :return:
        """
        try:
            sge_accounting = "/opt/sge/default/common/accounting"
            any_word = "[^:]+"
            job_string = "%s:%s:%s:%s:%s:%s:" % (
                queue_name, host_name, any_word,
                any_word, any_word, job_id
            )
            job = utils.find_line(sge_accounting, job_string)
            return job.split(":")
        except BaseException as e:
            raise exceptions.NotificationException(e=e)

    def set_job_accounting(self, accounting):
        """Add accounting line to the bdocker accounting file

        :param accounting: string with sge accounting format
        :return: empty array
        """
        try:
            exceptions.make_log("info",
                                "WRITING in %s" % self.bdocker_accounting)
            accounting_end_line = "%s\n" % accounting
            utils.add_to_file(self.bdocker_accounting, accounting_end_line)
            return []
        except BaseException as e:
            message = "ERROR UPDATING ACCOUNTING: %s. " % e.message
            exceptions.make_log("exception", message)
            raise exceptions.BatchException(message=message)


@six.add_metaclass(abc.ABCMeta)
class WNController(object):
    """Working node controller."""

    def __init__(self, conf):
        """Initialize controller.

        Set attributes and instanciate the Batch Notification
         Controller.

        :param conf: dictionary with configuration properties.
        :return:
        """
        self.conf = conf

    def conf_environment(self, session_data):
        """Configures the Working node environment by using CGROUPS.

        If cgroups control is enabled by using "enable_groups" option,
        it creates a cgroup and move the parent pid of the job to it.
        Only administration users can execute this method.

        :param session_data: job and user information
        :return: relevant information about the configuration.
        """
        raise exceptions.NoImplementedException(
            message="conf_environment is still not supported")

    def clean_environment(self, session_data, admin_token=None):
        """Clean the batch environment for the job.

        It deletes the cgroups created for the job.
        Only administration users can execute this method.

        :param session_data: job and user information
        :param admin_token: administration token.
        :return: True or False
        """
        raise exceptions.NoImplementedException(
            message="conf_environment is still not supported")

    def get_job_info(self):
        """Get job information.

        It is different for each batch scheduler, so, this class
        does not implement it.

        :return: dictionary with the relevant job information
        """
        raise exceptions.NoImplementedException(
            message="get_job_info is still not supported")


class CgroupsWNController(WNController):
    """Working node controller based in Cgroups."""

    def __init__(self, *args, **kwargs):
        super(CgroupsWNController, self).__init__(*args, **kwargs)
        try:
            self.enable_cgroups = self.conf.get("enable_cgroups",
                                                False)
            self.root_cgroup = self.conf.get("cgroups_dir",
                                             "/sys/fs/cgroup")
            self.parent_group = self.conf.get("parent_cgroup", '/')
            self.flush_time = self.conf.get("monitor_time", 10)
            self.only_docker_acc = self.conf.get(
                "only_docker_accounting", True
            )
            self.default_acc_file = LOCAL_ACCOUNTING_FILE
            accounting_conf = self.conf["accounting_endpoint"]
            self.notification_controller = BatchNotificationController(
                accounting_conf
            )
        except BaseException as e:
            raise exceptions.ConfigurationException(
                "CGROUP", e)

    @staticmethod
    def kill_job(spool):
        """Kill job

        It is different for each batch scheduler, so, this class
        does not implement it.

        :param spool:
        :return:
        """
        raise exceptions.NoImplementedException(
            message="kill_job is still not supported")

    @staticmethod
    def create_accounting_file(path, job_info):
        """Create accounting file with the relevant job information.

        It creates a yaml file by using the content of job_info.

        :param path: path in which store de file
        :param job_info: dictionary with job information
        :return:
        """
        try:
            utils.write_yaml_file(path, job_info)
        except BaseException as e:
            raise exceptions.BatchException(
                message="Creating accounting file",
                e=e)

    def _get_cgroup_job(self, job_id):
        """Generates the job cgroup location.

        :param job_id: Job identificator
        :return:
        """
        if self.parent_group == "/":
            cgroup_job = "/%s" % job_id
        else:
            cgroup_job = "%s/%s" % (self.parent_group, job_id)
        return cgroup_job

    def _create_cgroups(self, job_id, parent_pid):
        """Create CGROUPs realted to the job.

        It creates a cgroup in the parent cgroup (specified in
        configuration) naming it by using the job_idn. In addition,
        it creates another cgroup inside of previous one with name COMMON.
        The process pid of the job parent is included in COMMON.

        :param job_id: Job identificator
        :param parent_pid: process indentificator ot the
        job parent process.
        :return:
        """
        cgroups_utils.create_tree_cgroups(
            job_id,
            self.parent_group,
            root_parent=self.root_cgroup,
            pid=None)
        cgroup_job = self._get_cgroup_job(job_id)
        cgroups_utils.create_tree_cgroups(
            JOB_PROCESS_CGROUP,
            cgroup_job,
            root_parent=self.root_cgroup,
            pid=parent_pid)

    def _delete_cgroups(self, job_id):
        """Delete CGROUPs realted to the job.

        :param job_id:
        :return:
        """
        cgroup_job = self._get_cgroup_job(job_id)
        cgroups_utils.delete_tree_cgroups(
            JOB_PROCESS_CGROUP,
            cgroup_job,
            root_parent=self.root_cgroup)
        cgroups_utils.delete_tree_cgroups(
            job_id,
            self.parent_group,
            root_parent=self.root_cgroup
        )

    def track_accounting(self, file_path, job_id):
        """Get the accounting information from the cgroup.

        It retrieve the accounting information relative of job.

        :param job_id: job identificator
        :param file_path: location of the local accounting path
        :return: dictionary within accounting information
        """
        if self.enable_cgroups:
            track_acc = cgroups_utils.get_accounting(
                job_id,
                self.parent_group,
                root_parent=self.root_cgroup
            )
            if self.only_docker_acc:
                cgroup_job = self._get_cgroup_job(job_id)
                job_acc = cgroups_utils.get_accounting(
                    JOB_PROCESS_CGROUP,
                    cgroup_job,
                    root_parent=self.root_cgroup)
                track_acc ={
                    "memory_usage": (int(track_acc["memory_usage"]) -
                                     int(job_acc["memory_usage"])
                                     ),
                    "cpu_usage": (int(track_acc["cpu_usage"]) -
                                  int(job_acc["cpu_usage"])
                                  ),
                }
            utils.update_yaml_file(file_path, track_acc)

            return track_acc
        else:
            raise exceptions.NoImplementedException(
                message="Accounting not available without enabling"
                        "cgroups")

    def launch_job_monitoring(self, job_id, job_info, file_path, job_pid,
                              cpu_max=None,
                              mem_max=None):
        """It monitors job resources consumption

         It tracks the accounting and store it in a local accounting file.
         Furthermore, it controls that the job does not exeed the cpu and
        memory quota. In case the job pass any limit, it is deleted by
        killing the process associated to it.

        :param job_id: job identification, used to name the cgroup.
        :param job_info: relevant information useful to identify the job
        in the batch system accounting file.
        :param job_cgroup: job cgroups location
        :param file_path: location of the local accounting path
        :param job_pid: job process id.
        :param cpu_max: CPU quota limit.
        :param mem_max: memory quota limit.
        :return:
        """
        exceptions.make_log("info", "LAUNCH MONITORING Job: %s"
                            % job_id)
        try:
            pid = os.fork()
            if pid > 0:
                # Exit parent process
                return 0
            os.setsid()
        except OSError as e:
            message = "fork failed: %d (%s)" % (
                e.errno, e.strerror)
            exceptions.make_log("warning", message)
            raise exceptions.BatchException(
                message
            )
            # os.exit(1)
        exceptions.make_log("info", "MONITORING JOB %s." % job_id)
        self.create_accounting_file(file_path, job_info)
        while True:
            try:
                acc = self.track_accounting(file_path, job_id)
                if not acc:
                    break
                if cpu_max:
                    if int(acc["cpu_usage"]) >= int(cpu_max):
                        exceptions.make_log(
                            "exception",
                            "KILL JOB %s by CPU limit. Acc: %s. Max: %s" %
                            (job_id, acc["cpu_usage"],
                             cpu_max
                             ))
                        self.kill_job(job_pid)
                        break
                if mem_max:
                    if int(acc["memory_usage"]) >= int(mem_max):
                        exceptions.make_log(
                            "exception",
                            "KILL JOB %s by MEM limit. Acc: %s. Max: %s" %
                            (job_id, acc["memory_usage"],
                             mem_max
                             ))
                        self.kill_job(job_pid)
                        break

                exceptions.make_log("debug",
                                    "JOB CPU %s. Acc: %s. Max: %s" %
                                    (job_id, acc["cpu_usage"],
                                     cpu_max
                                     ))
                time.sleep(self.flush_time)
            except exceptions.CgroupException as e:
                exceptions.make_log("info", "MONITORING FINISHED")
                break
            except BaseException as e:
                message = "ERROR IN: %s. %s." % (file_path,
                                                 e.message)
                exceptions.make_log("exception", message)
                break

        child = os.getpid()
        os.kill(child, signal.SIG_IGN)
        time.sleep(0.1)

    def conf_environment(self, session_data, admin_token=None):
        """Configures the Working node environment by using CGROUPS.

        If cgroups control is enabled by using "enable_groups" option,
        it creates a cgroup and move the parent pid of the job to it.
        Only administration users can execute this method.

        :param session_data: job and user information
        :param admin_token: administration token.
        :return: relevant information about the configuration.
        """
        if self.enable_cgroups:
            try:
                job_id = session_data['job']['job_id']
                parent_pid = session_data['job']['parent_pid']
                user_home = session_data['home']
            except KeyError as e:
                message = ("Job information error %s"
                           % e.message)
                raise exceptions.ParseException(message=message)
            try:
                cgroup_job = self._get_cgroup_job(job_id)
                self._create_cgroups(job_id, parent_pid)
                acc_path = "%s/%s_%s" % (user_home,
                                         self.default_acc_file,
                                         job_id)
                batch_info = {"cgroup": cgroup_job,
                              "acc_file": acc_path}

                exceptions.make_log("debug",
                                    "CGROUP CONTROL ACTIVATED ON: %s "
                                    "JOB CGROUP: %s "
                                    % (self.parent_group, cgroup_job))
            except BaseException as e:
                raise exceptions.CgroupException(e=e)
        else:
            exceptions.make_log(
                "exception",
                "Accounting not available without enabling"
                " cgroups")
            batch_info = None
        return batch_info

    def clean_environment(self, session_data, admin_token=None):
        """Clean the batch environment for the job.

        It deletes the cgroups created for the job.
        Only administration users can execute this method.

        :param session_data: job and user information
        :param admin_token: administration token.
        :return: True or False
        """
        if self.enable_cgroups:
            try:
                flag = True
                job_id = session_data["job"]["job_id"]
                self._delete_cgroups(job_id)
            except BaseException as e:
                raise exceptions.CgroupException(e=e)
        else:
            exceptions.make_log(
                "exception",
                "Accounting not available without enabling"
                "cgroups")
            flag = False
        return flag

    def create_accounting_register(self, accounting_source):
        """Create a accounting register in bath system format.

        It is different for each batch scheduler, so, this class
        does not implement it.

        :param accounting_source: file path or dict with the information.
        :return: string with the accounting information
        """
        raise exceptions.NoImplementedException(
            message="get_job_info is still not supported")

    def notify_accounting(self, admin_token, accounting_source):
        """Submit job accounting information to the accounting server.

        Only administration users can execute this method.
        It generates the accounting message and sends it to the
        accounting server.

        :param admin_token: administration token
        :param accounting_source: accounting source.
        :return: response from the server
        """
        if self.enable_cgroups:
            try:
                exceptions.make_log("info",
                                    "CREATE ACCOUNTING STRING.")
                accounting = self.create_accounting_register(accounting_source)
                results = self.notification_controller.notify_accounting(
                    admin_token,
                    accounting)
                exceptions.make_log("info", "NOTIFIED.")
                return results
            except BaseException as e:
                raise exceptions.NotificationException(e=e)
        else:
            raise exceptions.NoImplementedException(
                message="Accounting not available without enabling"
                        "cgroups")


class SGEWNController(CgroupsWNController):
    """Working node controller based in SGE."""

    def __init__(self, *args, **kwargs):
        super(SGEWNController, self).__init__(*args, **kwargs)

    @staticmethod
    def _get_job_configuration(spool):
        """Private method to get the complete SGE job information.

        It gets the information related to relevant properties of the
        user and the job, including the job quotas.

        :param spool:
        :return:
        """
        path = "%s/config" % spool
        conf = utils.load_sge_job_configuration(path)
        qname = conf['queue']
        hostname = conf['host']
        logname = conf['job_owner']
        job_name = conf['job_name']
        account = conf['account']
        max_cpu = conf['h_cpu']
        submission_time = conf['submission_time']
        if max_cpu == "INFINITY":
            max_cpu = None
        else:
            max_cpu = parsers.parse_time_to_nanoseconds(
                max_cpu
            )
        max_memory = conf['h_data']
        if max_memory == "INFINITY":
            max_memory = None

        return {
            'queue_name': qname,
            'host_name': hostname,
            'log_name': logname,
            'job_name': job_name,
            'account_name': account,
            'max_cpu': max_cpu,
            'max_memory': max_memory,
            'submission_time': submission_time
        }

    @staticmethod
    def kill_job(job_pid):
        """Kill job

        It takes the job pid from the job spool directory and
        kills such process by using SIG.KILL signal.

        :param spool:
        :return:
        """
        try:
            job_pid_path = job_pid
            pid = utils.read_file(job_pid_path)
            if pid:
                pid = int(pid)
                os.kill(pid, signal.SIGKILL)
            return pid
        except BaseException as e:
            exc = exceptions.BatchException(
                message="COULD NOT KILL JOB",
                e=e)
            exceptions.make_log("exception", exc.message)
            raise exc

    def conf_environment(self, session_data, admin_token):
        """Configures the cgroup and the sge features.

        Only administration users can execute this method.
        It invoked the configuration of cgroup from WNController,
        in addition to launch the job monitoring functionality.

        :param session_data: job and user information
        :param admin_token: administration token.
        :return: relevant information about the configuration.
        """
        out = super(SGEWNController, self).conf_environment(session_data)
        if out:
            try:
                job = session_data['job']
                job_id = job['job_id']
                job_pid = "%s/job_pid" % job['spool']
                job_cpu_max = job['max_cpu']
                job_mem_max = job['max_memory']
                path = out["acc_file"]
                job_info = {
                    "job_id": job['job_id'],
                    "user_name": job['user_name'],
                    "queue_name": job['queue_name'],
                    "host_name": job['host_name'],
                    "job_name": job['job_name'],
                    "log_name": job['log_name'],
                    "account_name": job['account_name']
                }

                self.launch_job_monitoring(job_id, job_info, path,
                                           job_pid=job_pid,
                                           cpu_max=job_cpu_max,
                                           mem_max=job_mem_max)
            except KeyError as e:
                message = ("Job information error %s"
                           % e.message)
                raise exceptions.ParseException(message=message)
        return out

    def clean_environment(self, session_data, admin_token):
        """Clean the SGE batch environment for the job.

        Only administration users can execute this method.
        It deletes the cgroups created for the job.
        In addition it notify the accounting information to the
        accounting server, and clean the local accounting file.

        :param session_data: job and user information
        :param admin_token: administration token.
        :return: True or False
        """

        out = super(SGEWNController, self).clean_environment(session_data)
        if out:
            try:
                job_id = session_data["job"]["job_id"]
                acc_path = "%s/%s_%s" % (session_data['home'],
                                         self.default_acc_file,
                                         job_id)
                self.notify_accounting(admin_token, acc_path)
                utils.delete_file(acc_path)
            except KeyError as e:
                message = ("Job information error %s"
                           % e.message)
                raise exceptions.ParseException(message=message)
            except BaseException as e:
                message = ("ACCOUNTING NOTIFICATION ERROR %s"
                           % e.message)
                raise exceptions.BatchException(message=message)

    def create_accounting_register(self, accounting_source):
        """Create a accounting register in SGE bath system format.

        It retrieves a string following the same format than the SGE accounting
        file.

        :param accounting_source: file path or dict with the information.
        :return: string with the accounting information
        """
        try:
            job = utils.read_yaml_file(accounting_source)
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

    def get_job_info(self):
        """Get job information.

        It retrieves the relevant information related to the job
        and the its execution environment.

        :return: dictionary with the relevant job information
        """
        try:
            job_id = utils.get_environment(
                'JOB_ID')
            home = os.path.realpath(utils.get_environment(
                'HOME'))
            user = utils.get_environment(
                'USER')
            spool_dir = utils.get_environment(
                "SGE_JOB_SPOOL_DIR")
            parent_pid = utils.read_file(
                "%s/pid" % spool_dir)
            job_info = {'home': home,
                        'job_id': job_id,
                        'user_name': user,
                        'spool': spool_dir,
                        'parent_pid': parent_pid
                        }
            job_info.update(self._get_job_configuration(spool_dir))
            return job_info
        except BaseException as e:
            raise exceptions.BatchException("Get job information", e=e)
