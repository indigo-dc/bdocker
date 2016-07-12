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

import uuid

import cgroupspy
import mock
import testtools

from bdocker import exceptions as bdocker_exceptions
from bdocker.modules import cgroups_utils


class TestCgroups(testtools.TestCase):
    """Test SGE Batch controller."""
    def setUp(self):
        super(TestCgroups, self).setUp()
        self.parent_path = "/systemd/user/"

    @mock.patch.object(cgroupspy.trees.GroupedTree, "__init__")
    @mock.patch.object(cgroupspy.trees.GroupedTree, "get_node_by_path")
    @mock.patch.object(cgroupspy.nodes.Node, "create_cgroup")
    @mock.patch("bdocker.modules.cgroups_utils.task_to_cgroup")
    def test_create_tree_cgroup(self, m_add, m_cre, m_path, m_tree):
        gnodes = cgroupspy.nodes.NodeControlGroup("na")
        gnodes.nodes = [cgroupspy.nodes.Node]
        m_path.side_effect = [gnodes]
        m_tree.return_value = None
        out = cgroups_utils.create_tree_cgroups(
            "66",
            self.parent_path,
            pid='19858'
        )
        self.assertIsNone(out)
        self.assertEqual(
            self.parent_path,
            m_path.call_args_list[0][0][0]
        )
        self.assertEqual(1, m_add.call_count)

    @mock.patch.object(cgroupspy.trees.GroupedTree, "__init__")
    @mock.patch.object(cgroupspy.trees.GroupedTree, "get_node_by_path")
    @mock.patch.object(cgroupspy.nodes.Node, "create_cgroup")
    @mock.patch("bdocker.modules.cgroups_utils.task_to_cgroup")
    def test_create_tree_cgroup_several(self, m_add, m_cre, m_path, m_tree):
        gnodes = cgroupspy.nodes.NodeControlGroup("na")
        gnodes.nodes = [cgroupspy.nodes.Node,
                        cgroupspy.nodes.Node
                        ]
        m_path.side_effect = [gnodes]
        m_tree.return_value = None
        out = cgroups_utils.create_tree_cgroups(
            "66",
            self.parent_path,
            pid='19858'
        )
        self.assertIsNone(out)
        self.assertEqual(
            self.parent_path,
            m_path.call_args_list[0][0][0]
        )
        self.assertEqual(2, m_add.call_count)

    @mock.patch.object(cgroupspy.trees.GroupedTree, "__init__")
    @mock.patch.object(cgroupspy.trees.GroupedTree, "get_node_by_path")
    @mock.patch.object(cgroupspy.nodes.Node, "create_cgroup")
    @mock.patch("bdocker.modules.cgroups_utils.task_to_cgroup")
    def test_create_tree_cgroup_exception(self, m_add, m_cre, m_path, m_tree):
        gnodes = cgroupspy.nodes.NodeControlGroup("na")
        gnodes.nodes = [cgroupspy.nodes.Node]
        m_path.side_effect = [gnodes,
                              ]
        m_cre.side_effect = OSError(13, "err", "file")
        m_tree.return_value = None
        self.assertRaises(bdocker_exceptions.CgroupException,
                          cgroups_utils.create_tree_cgroups,
                          "66",
                          self.parent_path,
                          pid='19858',
                          )

    @mock.patch.object(cgroupspy.trees.GroupedTree, "__init__")
    @mock.patch.object(cgroupspy.trees.GroupedTree,
                       "get_node_by_path")
    @mock.patch.object(cgroupspy.nodes.Node, "delete_cgroup")
    @mock.patch("bdocker.modules.cgroups_utils.task_to_cgroup")
    @mock.patch("bdocker.utils.read_file")
    def test_delete_tree_cgroup(self, m_rad, m_task, m_del, m_path, m_tree):
        gnodes = cgroupspy.nodes.NodeControlGroup("na")
        parent_node = cgroupspy.nodes.Node("parent")
        gnodes.nodes = [cgroupspy.nodes.Node("",
                                             parent=parent_node)]
        m_path.side_effect = [gnodes]
        m_tree.return_value = None
        name = uuid.uuid4().hex
        out = cgroups_utils.delete_tree_cgroups(
            name,
            self.parent_path
        )
        self.assertIsNone(out)
        self.assertEqual(1, m_del.call_count)
        self.assertEqual(
            name,
            m_del.call_args_list[0][0][0]
        )
        self.assertEqual(1, m_path.call_count)
        self.assertEqual(
            self.parent_path,
            m_path.call_args_list[0][0][0]
        )

    @mock.patch.object(cgroupspy.trees.GroupedTree, "__init__")
    @mock.patch.object(cgroupspy.trees.GroupedTree,
                       "get_node_by_path")
    @mock.patch.object(cgroupspy.nodes.Node, "delete_cgroup")
    @mock.patch("bdocker.modules.cgroups_utils.task_to_cgroup")
    @mock.patch("bdocker.utils.read_file")
    def test_delete_tree_cgroup_several_nodes(self, m_rad,
                                              m_task, m_del, m_path,
                                              m_tree):
        gnodes = cgroupspy.nodes.NodeControlGroup("na")
        parent_node = cgroupspy.nodes.Node("parent")
        gnodes.nodes = [cgroupspy.nodes.Node("", parent=parent_node),
                        cgroupspy.nodes.Node("", parent=parent_node)]
        m_path.side_effect = [gnodes,
                              ]
        m_tree.return_value = None
        name = uuid.uuid4().hex
        out = cgroups_utils.delete_tree_cgroups(
            name,
            self.parent_path
        )
        self.assertIsNone(out)
        self.assertEqual(2, m_del.call_count)
        self.assertEqual(
            name,
            m_del.call_args_list[0][0][0]
        )
        self.assertEqual(1, m_path.call_count)
        self.assertEqual(
            self.parent_path,
            m_path.call_args_list[0][0][0]
        )

    @mock.patch.object(cgroupspy.trees.GroupedTree, "__init__")
    @mock.patch.object(cgroupspy.trees.Tree, "get_node_by_path")
    @mock.patch.object(cgroupspy.nodes.Node, "create_cgroup")
    @mock.patch("bdocker.utils.add_to_file")
    def test_create_cgroup(self, m_add, m_cre, m_path, m_tree):
        m_path.side_effect = [cgroupspy.nodes.Node,
                              ]
        parent_groups = ["systemd/user"]
        out = cgroups_utils.create_cgroups("66",
                                           parent_groups,
                                           pid='19858'
                                           )
        m_tree.return_value = None
        self.assertIsNone(out)
        self.assertEqual(
            "/%s/" % parent_groups[0],
            m_path.call_args_list[0][0][0]
        )
        self.assertEqual(parent_groups.__len__(), m_add.call_count)
        # I have problems controlling how many
        # times the create method is exected

    @mock.patch.object(cgroupspy.trees.GroupedTree, "__init__")
    @mock.patch.object(cgroupspy.trees.Tree, "get_node_by_path")
    @mock.patch.object(cgroupspy.nodes.Node, "create_cgroup")
    @mock.patch("bdocker.utils.add_to_file")
    def test_create_cgroup_several_parents(self, m_add, m_cre, m_path,
                                           m_tree):
        m_path.side_effect = [cgroupspy.nodes.Node,
                              cgroupspy.nodes.Node,
                              cgroupspy.nodes.Node]
        parent_groups = ["systemd/user", "foo", "cpu"]
        name = uuid.uuid4().hex
        m_tree.return_value = None
        out = cgroups_utils.create_cgroups(name,
                                           parent_groups,
                                           pid='19858'
                                           )
        self.assertIsNone(out)
        self.assertEqual(parent_groups.__len__(), m_cre.call_count)
        self.assertEqual(
            name,
            m_cre.call_args_list[0][0][0]
        )
        self.assertEqual(
            name,
            m_cre.call_args_list[1][0][0]
        )
        self.assertEqual(
            name,
            m_cre.call_args_list[2][0][0]
        )
        self.assertEqual(parent_groups.__len__(), m_add.call_count)
        self.assertEqual(
            "/%s/" % parent_groups[0],
            m_path.call_args_list[0][0][0]
        )
        self.assertEqual(
            "/%s/" % parent_groups[1],
            m_path.call_args_list[1][0][0]
        )
        self.assertEqual(
            "/%s/" % parent_groups[2],
            m_path.call_args_list[2][0][0]
        )

    @mock.patch.object(cgroupspy.trees.Tree, "get_node_by_path")
    @mock.patch.object(cgroupspy.nodes.Node, "create_cgroup")
    @mock.patch("bdocker.utils.add_to_file")
    def test_create_cgroup_no_pid(self, m_add, m_cre, m_path):
        m_path.side_effect = [cgroupspy.nodes.Node,
                              cgroupspy.nodes.Node,
                              cgroupspy.nodes.Node]
        parent_groups = ["systemd/user", "cpu"]
        name = uuid.uuid4().hex
        out = cgroups_utils.create_cgroups(
            name,
            parent_groups,
        )
        self.assertIsNone(out)
        self.assertEqual(parent_groups.__len__(), m_cre.call_count)
        self.assertEqual(
            name,
            m_cre.call_args_list[0][0][0]
        )
        self.assertEqual(
            name,
            m_cre.call_args_list[1][0][0]
        )
        self.assertEqual(parent_groups.__len__(), m_path.call_count)
        self.assertEqual(
            "/%s/" % parent_groups[0],
            m_path.call_args_list[0][0][0]
        )
        self.assertEqual(
            "/%s/" % parent_groups[1],
            m_path.call_args_list[1][0][0]
        )
        self.assertEqual(0, m_add.call_count)

    @mock.patch.object(cgroupspy.trees.Tree, "get_node_by_path")
    @mock.patch.object(cgroupspy.nodes.Node, "delete_cgroup")
    def test_delete_cgroup(self, m_del, m_path):
        m_path.side_effect = [cgroupspy.nodes.Node]
        parent_groups = ["foo"]
        name = uuid.uuid4().hex
        out = cgroups_utils.delete_cgroups(
            name,
            parent_groups
        )
        self.assertIsNone(out)
        self.assertEqual(parent_groups.__len__(), m_del.call_count)
        self.assertEqual(
            name,
            m_del.call_args_list[0][0][0]
        )
        self.assertEqual(1, m_path.call_count)
        self.assertEqual(
            "/%s/" % parent_groups[0],
            m_path.call_args_list[0][0][0]
        )

    @mock.patch.object(cgroupspy.trees.Tree, "get_node_by_path")
    @mock.patch.object(cgroupspy.nodes.Node, "delete_cgroup")
    def test_delete_cgroup_several_parents(self, m_del, m_path):
        m_path.side_effect = [cgroupspy.nodes.Node,
                              cgroupspy.nodes.Node]
        parent_groups = ["foo", "joo"]
        name = uuid.uuid4().hex
        out = cgroups_utils.delete_cgroups(name,
                                           parent_groups
                                           )
        self.assertIsNone(out)
        self.assertEqual(parent_groups.__len__(), m_del.call_count)
        self.assertEqual(
            name,
            m_del.call_args_list[0][0][0]
        )
        self.assertEqual(
            name,
            m_del.call_args_list[1][0][0]
        )
        self.assertEqual(parent_groups.__len__(), m_path.call_count)
        self.assertEqual(
            "/%s/" % parent_groups[0],
            m_path.call_args_list[0][0][0]
        )
        self.assertEqual(
            "/%s/" % parent_groups[1],
            m_path.call_args_list[1][0][0]
        )
