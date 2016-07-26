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

from cgroupspy import trees

from bdocker import exceptions
from bdocker import utils


def get_pids_from_cgroup(cgroup):
    tasks_path = "%s/tasks" % cgroup
    job_pids = utils.read_file(tasks_path)
    array_pids = job_pids.split()
    return array_pids


def task_to_cgroup(cgroup_dir, pid):
    tasks = "NO TASK FILE"
    try:
        tasks = "%s/tasks" % cgroup_dir
        utils.add_to_file(tasks, pid)
    except IOError as e:
        if e.errno == 28:
            # IOError: [Errno 28] No space left on device
            exceptions.make_log("warning", e.message)
        else:
            exceptions.make_log("exception",
                                "Error when assign %s to %s. %s"
                                % (pid, tasks, e.message))


def remove_tasks(cgroup_name, cgroup_parent):
    child_path = "%s/%s" % (cgroup_parent, cgroup_name)
    job_pids = get_pids_from_cgroup(child_path)
    for pid in job_pids:
        task_to_cgroup(cgroup_parent, pid)


def parse_cgroup_name(name):
    """Clean cgroup name.

    It is needed because cgroupspy clean them.

    :param name:
    :return: name without extensions
    """
    extensions = ['.slice', '.scope', '.partition']
    new_name = str(name)
    for ex in extensions:
        new_name = new_name.replace(ex, "")
    return new_name


def create_tree_cgroups(group_name, parent_group_dir,
                        pid=None,
                        root_parent="/sys/fs/cgroup"):
    try:
        c_trees = trees.GroupedTree(root_path=root_parent)
        parent_group = parse_cgroup_name(parent_group_dir)
        parent_node = c_trees.get_node_by_path(parent_group)
        if parent_node:
            for node in parent_node.nodes:
                try:
                    new_node = node.create_cgroup(group_name)
                    if pid:
                        task_to_cgroup(new_node.full_path, pid)
                except OSError as e:
                    if e.errno == 17:
                        exceptions.make_log("warning", e.message,
                                            group_name)
                    else:
                        raise e
        else:
            raise exceptions.BatchException(
                "Not found cgroup parent: %s,"
                " in root: %s"
                % (parent_group_dir, root_parent))
    except BaseException as e:
        exc = exceptions.CgroupException(e)
        exceptions.make_log("exception", "CGROUPS creation problem. %s"
                            % exc.message, group_name)
        raise exc


def delete_tree_cgroups(group_name, parent_group,
                        root_parent="/sys/fs/cgroup"):
    try:
        c_trees = trees.GroupedTree(root_path=root_parent)
        parent_group = parse_cgroup_name(parent_group)
        parent_node = c_trees.get_node_by_path(parent_group)
        for node in parent_node.nodes:
            try:
                remove_tasks(group_name, node.full_path)
                node.delete_cgroup(group_name)
            except IOError as e:
                if e.errno == 2:
                    exceptions.make_log("warning", e.message,
                                        group_name)
                else:
                    raise e
    except BaseException as e:
        exc = exceptions.CgroupException(e)
        exceptions.make_log("exception", "CGROUPS delete problem. %s"
                            % exc.message, group_name)
        raise exc


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
        exc = exceptions.CgroupException(e)
        exceptions.make_log("exception", "CGROUPS creation problem. %s"
                            % exc.message, group_name)
        raise exc


def delete_cgroups(group_name, parent_groups,
                   root_parent="/sys/fs/cgroup"):
    try:
        c_tree = trees.Tree(root_path=root_parent)
        for parent in parent_groups:
            parent = "/%s/" % parent
            parent_node = c_tree.get_node_by_path(parent)
            parent_node.delete_cgroup(group_name)
    except BaseException as e:
        exc = exceptions.CgroupException(e)
        exceptions.make_log("exception", "CGROUPS delete problem. %s"
                            % exc.message, group_name)
        raise exc


def get_accounting(group_name, parent_group,
                   root_parent="/sys/fs/cgroup"):
    memory_file = "%s/memory%s/%s/memory.usage_in_bytes" % (
        root_parent, parent_group, group_name
    )
    cpu_file = "%s/cpuacct%s/%s/cpuacct.usage" % (
        root_parent, parent_group, group_name
    )
    try:
        memory_usage = utils.read_file(memory_file)
        cpu_usage = utils.read_file(cpu_file)
    except BaseException:
        raise exceptions.CgroupException("%s/%s Not found"
                                         % (parent_group,
                                            group_name)
                                         , group_name)
    return {"memory_usage": memory_usage,
            "cpu_usage": cpu_usage}
