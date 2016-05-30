# -*- coding: utf-8 -*-

# Copyright 2016 LIP - Lisbon
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
from cgroupspy import trees
import os

from bdocker.common import utils


class BatchController(object):

    def __init__(self):
        pass

    def get_job_info(self):
        return "retrieving job info"

    def get_cuotas(self):
        return "retrieving cuotas"


class SGEController(BatchController):

    def __init__(self, path):
        self.path = path

    def _create_cgroup(self, group_name):
        c_tree = trees.Tree()
        parent_node = c_tree.get_node_by_path(self.path)
        node = parent_node.create_cgroup(group_name)

    def _delete_cgroup(self, group_name):
        c_tree = trees.Tree()
        parent_node = c_tree.get_node_by_path(self.path)
        node = parent_node.delete_cgroup(group_name)

    def _get_cgroup(self, job_id):
        spool_dir = os.getenv("SGE_JOB_SPOOL_DIR", None)
        job_pid = utils.read_file("%s/job_pid" % spool_dir)
        cgroup_file = "/proc/%/cgroup" % job_pid
        p_cgroup = utils.read_file(cgroup_file)

        # 10:devices:/system.slice/sgeexecd.service
        # 9:perf_event:/
        # 8:cpuset:/
        # 7:memory:/system.slice/sgeexecd.service
        # 6:net_cls:/
        # 5:cpuacct,cpu:/system.slice/sgeexecd.service
        # 4:freezer:/
        # 3:blkio:/system.slice/sgeexecd.service
        # 2:hugetlb:/
        # 1:name=systemd:/system.slice/sgeexecd.service

        cgroup = "/sys/fs/cgroup/" % p_cgroup
        job_id = utils.read_file("%s/job_pid" % spool_dir)
        return None

    def get_job_info(self):
        job_id = os.getenv(
            'JOB_ID', None)
        home = os.path.realpath(os.getenv(
            'HOME', None))
        user = os.getenv(
            'USER', None)

        cgroup = self._get_cgroup(job_id)
        return {'home': home,
                'job_id': job_id,
                'user': user,
                'cgroup':cgroup
                }