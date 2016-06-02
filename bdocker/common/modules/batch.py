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
import logging
import os

from bdocker.common import exceptions
from bdocker.common import utils
LOG = logging.getLogger(__name__)


def task_to_cgroup(cgroup_dir, pid):
    try:
        tasks = "%s/tasks" % cgroup_dir
        utils.add_to_file(tasks, pid)
    except IOError as e:
        LOG.exception("Error when assign %s to %s. %s"
                      %(pid, tasks, e.message))


def create_tree_cgroups(group_name, parent_group,
                        pid=None,
                        root_parent="/sys/fs/cgroup"):
    try:
        c_trees = trees.GroupedTree(root_path=root_parent)
        parent_node = c_trees.get_node_by_path(parent_group)
        if parent_node:
            for node in parent_node.nodes:
                new_node = node.create_cgroup(group_name)
                if pid:
                    task_to_cgroup(new_node.full_path, pid)
        else:
            raise exceptions.BatchException("Not found cgroup parent: %s,"
                                            " in root: %s"
                                            % (parent_group, root_parent))
    except BaseException as e:
        LOG.exception("CGROUPS creation problem. %s"
                      % e.message)
        raise exceptions.DockerException(e)


def delete_tree_cgroups(group_name, parent_group,
                         pid=None,
                         root_parent="/sys/fs/cgroup"):
    try:
        c_trees = trees.GroupedTree(root_path=root_parent)
        parent_node = c_trees.get_node_by_path(parent_group)
        for node in parent_node.nodes:
            node.delete_cgroup(group_name)
    except BaseException as e:
        LOG.exception("CGROUPS delete problem. %s"
                      % e.message)
        raise exceptions.DockerException(e)


def create_cgroups(group_name, parent_groups, pid=None,
                  root_parent="/sys/fs/cgroup"):
    try:
        c_tree = trees.Tree(root_path=root_parent)
        # test it GroupedTree
        for parent in parent_groups:
            parent = "/%s/" % parent
            parent_node = c_tree.get_node_by_path(parent)
            node = parent_node.create_cgroup(group_name)
            if pid:
                task_to_cgroup(node.full_path, pid)
    except BaseException as e:
        LOG.exception("CGROUPS creation problem. %s"
                      % e.message)
        raise exceptions.DockerException(e)


def delete_cgroups(group_name, parent_groups,
                  root_parent="/sys/fs/cgroup"):
    try:
        c_tree = trees.Tree(root_path=root_parent)
        for parent in parent_groups:
            parent = "/%s/" % parent
            parent_node = c_tree.get_node_by_path(parent)
            parent_node.delete_cgroup(group_name)
    except BaseException as e:
        LOG.exception("CGROUPS delete problem. %s"
                      % e.message)
        raise exceptions.DockerException(e)


class BatchController(object):

    def __init__(self):
        pass

    def get_job_info(self):
        return "retrieving job info"

    def get_cuotas(self):
        return "retrieving cuotas"


class SGEController(BatchController):

    def __init__(self, conf):
        self.enable_cgroups = conf.get("enable_cgroups",
                                    False)
        self.root_cgroup = conf.get("cgroups_dir",
                                    "/sys/fs/cgroup")
        self.parent_group = conf.get("parent_cgroup", '/')

    def conf_environment(self, job_id, spool_dir):
        if self.enable_cgroups:
            LOG.exception("CGROUP CONTROL ACTIVATED ON: %s "
                     % self.parent_group)
            parent_pid = utils.read_file("%s/pid" % spool_dir)
            create_tree_cgroups(job_id,
                                self.parent_group,
                                root_parent=self.root_cgroup,
                                pid=parent_pid)
            if self.parent_group == "/":
                cgroup_parent = "/%s" % job_id
            else:
                cgroup_parent = "%s/%s" % (self.parent_group, job_id)

        else:
            LOG.exception("CGROUP CONTROL NOT ACTIVATED")
            cgroup_parent = None
        LOG.exception("CGROUP is %s" % cgroup_parent)
        return cgroup_parent

    def clean_environment(self, job_id):
        # TODO(jorgesece): it is needed to delete or auto?
        # TODO(jorgesece): Analize when delete it, if has processes error
        # WE COULD CHANGE THEM TO SGEEX.SERVICE/tasks
        if self.enable_cgroups:
            delete_tree_cgroups(job_id,
                                self.parent_group,
                                root_parent=self.root_cgroup)

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
