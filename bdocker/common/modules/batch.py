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


def create_cgroups(group_name, parent_groups, pid=None,
                  root_parent="/sys/fs/cgroup"):
    c_tree = trees.Tree(root_path=root_parent)
    # test it GroupedTree
    for parent in parent_groups:
        parent = "/%s/" % parent
        parent_node = c_tree.get_node_by_path(parent)
        node = parent_node.create_cgroup(group_name)
        if pid:
            tasks = "%s/tasks" % node.full_path
            utils.add_to_file(tasks, pid)


def delete_cgroups(group_name, parent_groups,
                  root_parent="/sys/fs/cgroup"):
    c_tree = trees.Tree(root_path=root_parent)
    for parent in parent_groups:
        parent = "/%s/" % parent
        parent_node = c_tree.get_node_by_path(parent)
        parent_node.delete_cgroup(group_name)


class BatchController(object):

    def __init__(self):
        pass

    def get_job_info(self):
        return "retrieving job info"

    def get_cuotas(self):
        return "retrieving cuotas"


class SGEController(BatchController):

    def __init__(self, conf):
        root_cgroup = conf.get("cgroup", None)
        self.root_cgroup = root_cgroup

    def conf_environment(self, job_id):
        if self.root_cgroup:
            spool_dir = os.getenv("SGE_JOB_SPOOL_DIR")
            parent_pid = utils.read_file("%s/pid" % spool_dir)
            parent_groups = ['/cpu/']
            create_cgroups(job_id,
                           parent_groups,
                           root_parent=self.root_cgroup,
                           pid=parent_pid)

    def clean_environment(self, job_id):
        # TODO(jorgesece): it is needed to delete or auto?
        # TODO(jorgesece): Analize when delete it, if has processes error
        # WE COULD CHANGE THEM TO SGEEX.SERVICE/tasks
        if self.root_cgroup:
            parent_groups = ['/cpu/']
            delete_cgroups(job_id,
                           parent_groups,
                           self.root_cgroup)

    def get_job_info(self):
        job_id = os.getenv(
            'JOB_ID', None)
        home = os.path.realpath(os.getenv(
            'HOME', None))
        user = os.getenv(
            'USER', None)

        # cgroup = self._get_cgroup(job_id)
        return {'home': home,
                'job_id': job_id,
                'user': user,
                # 'cgroup':cgroup
                }

    # def _get_cgroup(self, job_id):
    #     spool_dir = os.getenv("SGE_JOB_SPOOL_DIR", None)
    #     job_pid = utils.read_file("%s/job_pid" % spool_dir)
    #     cgroup_file = "/proc/%/cgroup" % job_pid
    #     p_cgroup = utils.read_file(cgroup_file)
    #
    #     # 10:devices:/system.slice/sgeexecd.service
    #     # 9:perf_event:/
    #     # 8:cpuset:/
    #     # 7:memory:/system.slice/sgeexecd.service
    #     # 6:net_cls:/
    #     # 5:cpuacct,cpu:/system.slice/sgeexecd.service
    #     # 4:freezer:/
    #     # 3:blkio:/system.slice/sgeexecd.service
    #     # 2:hugetlb:/
    #     # 1:name=systemd:/system.slice/sgeexecd.service
    #
    #     cgroup = "/sys/fs/cgroup/" % p_cgroup
    #     job_id = utils.read_file("%s/job_pid" % spool_dir)
    #     return None
