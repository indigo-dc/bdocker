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

import cgroupspy
import mock
import testtools
import uuid

from bdocker.common.modules import batch



class TestSGEController(testtools.TestCase):
    """Test SGE Batch controller."""
    def setUp(self):
        super(TestSGEController, self).setUp()
        self.parent_path = "/systemd/user/"
        # self.control = batch.SGEController({})

    @mock.patch.object(cgroupspy.trees.Tree, "get_node_by_path")
    @mock.patch.object(cgroupspy.nodes.Node, "create_cgroup")
    @mock.patch("bdocker.common.utils.add_to_file")
    def test_create_cgroup(self, m_add, m_cre, m_path):
        m_path.side_effect = [cgroupspy.nodes.Node,
                              ]
        parent_groups = ["systemd/user"]
        out = batch.create_cgroups("66",
                                   parent_groups,
                                   pid='19858'
                                   )
        self.assertIsNone(out)
        self.assertEqual(
            "/%s/" % parent_groups[0],
            m_path.call_args_list[0][0][0]
        )
        self.assertEqual(parent_groups.__len__(), m_add.call_count)
        # I have problems controlling how many times the create method is exected

    @mock.patch.object(cgroupspy.trees.Tree, "get_node_by_path")
    @mock.patch.object(cgroupspy.nodes.Node, "create_cgroup")
    @mock.patch("bdocker.common.utils.add_to_file")
    def test_create_cgroup_several_parents(self, m_add, m_cre, m_path):
        m_path.side_effect = [cgroupspy.nodes.Node,
                              cgroupspy.nodes.Node,
                              cgroupspy.nodes.Node]
        parent_groups = ["systemd/user", "foo", "cpu"]
        name = uuid.uuid4().hex
        out = batch.create_cgroups(name,
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
    @mock.patch("bdocker.common.utils.add_to_file")
    def test_create_cgroup_no_pid(self, m_add, m_cre, m_path):
        m_path.side_effect = [cgroupspy.nodes.Node,
                              cgroupspy.nodes.Node,
                              cgroupspy.nodes.Node]
        parent_groups = ["systemd/user", "cpu"]
        name = uuid.uuid4().hex
        out = batch.create_cgroups(name,
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

    @mock.patch.object(cgroupspy.trees.Tree,"get_node_by_path")
    @mock.patch.object(cgroupspy.nodes.Node,"delete_cgroup")
    def test_delete_cgroup(self,m_del, m_path):
        m_path.side_effect = [cgroupspy.nodes.Node]
        parent_groups = ["foo"]
        name = uuid.uuid4().hex
        out = batch.delete_cgroups(name,
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


    @mock.patch.object(cgroupspy.trees.Tree,"get_node_by_path")
    @mock.patch.object(cgroupspy.nodes.Node,"delete_cgroup")
    def test_delete_cgroup_several_parents(self, m_del, m_path):
        m_path.side_effect = [cgroupspy.nodes.Node,
                              cgroupspy.nodes.Node]
        parent_groups = ["foo", "joo"]
        name = uuid.uuid4().hex
        out = batch.delete_cgroups(name,
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

    def test_clean_environment(self):
        pass

    def test_conf_environment(self):
        pass

    def test_get_job_info(self):
        pass