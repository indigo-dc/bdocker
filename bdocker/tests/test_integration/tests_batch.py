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
from cgroupspy import trees
import testtools

from bdocker.common.modules import batch
from bdocker.common import utils



class TestSGEController(testtools.TestCase):
    """Test SGE Batch controller."""
    def setUp(self):
        super(TestSGEController, self).setUp()
        self.name = "bdocker.test"
        self.parent = "/user"
        # self.control = batch.SGEController({})

    def test_create_cgroup(self):
        conf = {"enable_cgroups": True,
                "parent_cgroup": "/user/1000.user/"
                }
        job_id = 33
        spool = "/home/jorge/FAKE_JOB"
        controller = batch.SGEController(conf)
        out = controller.conf_environment(job_id=job_id,
                                    spool_dir=spool
                                    )
        expected = {"cgroup": "/user/1000.user/%s" % job_id}
        self.assertEqual(expected, out)

    def test_create_cgroup(self):
        parent_groups = self.parent
        out = batch.create_tree_cgroups(self.name,
                                  parent_groups,
                                  pid='30084'
                                  )
        self.assertIsNone(out)

    def test_delete_cgroup(self):
        parent_groups = self.parent
        out = batch.delete_tree_cgroups(self.name,
                                   parent_groups
                                   )
        self.assertIsNone(out)

    def test_treeGroups(self):
        c_trees = trees.GroupedTree()
        list_node = []
        print("nodes")
#        for node in c_trees.walk():
#            list_node.append(node.path)
        print("docker")
        parent_node = c_trees.get_node_by_path("/docker")
        if parent_node:
            print(parent_node.path)
        print
        list_1 = []
        for node in parent_node.nodes:
            if node:
                list_1.append(node.path)
                print(node.path)
        print("/user/1000.user/")
        parent_node = c_trees.get_node_by_path("/user/1000.user/")
        if parent_node:
            print(parent_node.path)
        list_2 = []
        for node in parent_node.nodes:
            if node:
                list_2.append(node.path)
                print(node.path)


    def test_create_cgroup_several_pids(self):

        out = batch.create_tree_cgroups(self.name,
                                  self.parent,
                                    pid="12823"
                                  )
        cgroup_job = "/sys/fs/cgroup/cpu%s/%s" % (
            self.parent, self.name
        )
        batch.task_to_cgroup(cgroup_job,"12824")
        self.assertIsNone(out)

    def test_delete_cgroup_serveral_pids(self):
        # cgroup_job = "%s/%s/tasks" % (self.parent, self.name)
        # read from job cgroup
        # job_pids = utils.read_file(cgroup_job)
        # # add
        # batch.task_to_cgroup(self.parent,job_pids)
        out = batch.delete_tree_cgroups(self.name,
                                        self.parent
                                        )
        self.assertIsNone(out)

if __name__ == '__main__':
    testtools.sys.argv.insert(1,'--verbose')
    testtools.main(argv = testtools.sys.argv)