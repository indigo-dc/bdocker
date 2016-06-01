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



class TestSGEController(testtools.TestCase):
    """Test SGE Batch controller."""
    def setUp(self):
        super(TestSGEController, self).setUp()
        self.parent_path = "/systemd/user/"
        # self.control = batch.SGEController({})

    def test_create_cgroup(self):
        parent_groups = ["/systemd/user/"]
        out = batch.create_cgroups("66",
                                  parent_groups,
                                  pid='19858'
                                  )
        self.assertIsNone(out)

    def test_delete_cgroup(self):
        parent_groups = ["/systemd/user/"]
        out = batch.delete_cgroups("66",
                                   parent_groups
                                   )
        self.assertIsNone(out)

    def test_treeGroups(self):
        c_trees = trees.GroupedTree()
        list_node = []
        print("nodes")
#        for node in c_trees.walk():
#            list_node.append(node.path)
        print("system.slice")
        parent_node = c_trees.get_node_by_path("/system.slice")
        if parent_node:
            print(parent_node.path)
        print
        list_1 = []
        for node in parent_node.nodes:
            if node:
                list_1.append(node.path)
                print(node.path)
        print("system.slice/docker.service")
        parent_node = c_trees.get_node_by_path("/system.slice/docker.service")
        if parent_node:
            print(parent_node.path)
        list_2 = []
        for node in parent_node.nodes:
            if node:
                list_2.append(node.path)
                print(node.path)


if __name__ == '__main__':
    testtools.sys.argv.insert(1,'--verbose')
    testtools.main(argv = testtools.sys.argv)