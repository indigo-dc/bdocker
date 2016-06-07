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
import exceptions
import mock
import os
import testtools
import uuid

from bdocker.common.modules import batch
from bdocker.common import exceptions as bdocker_exceptions


class TestSGEController(testtools.TestCase):
    """Test SGE Batch controller."""
    def setUp(self):
        super(TestSGEController, self).setUp()
        self.parent_path = "/systemd/user/"


    @mock.patch.object(cgroupspy.trees.GroupedTree, "get_node_by_path")
    @mock.patch.object(cgroupspy.nodes.Node, "create_cgroup")
    @mock.patch("bdocker.common.modules.batch.task_to_cgroup")
    def test_create_tree_cgroup(self, m_add, m_cre, m_path):
        gnodes = cgroupspy.nodes.NodeControlGroup("na")
        gnodes.nodes = [cgroupspy.nodes.Node]
        m_path.side_effect = [gnodes,
                              ]
        #m_cre.side_effect = exceptions.OSError(13, "err", "file")

        out = batch.create_tree_cgroups("66",
                                   self.parent_path,
                                   pid='19858'
                                   )
        self.assertIsNone(out)
        self.assertEqual(
            self.parent_path,
            m_path.call_args_list[0][0][0]
        )
        self.assertEqual(1, m_add.call_count)

    @mock.patch.object(cgroupspy.trees.GroupedTree, "get_node_by_path")
    @mock.patch.object(cgroupspy.nodes.Node, "create_cgroup")
    @mock.patch("bdocker.common.modules.batch.task_to_cgroup")
    def test_create_tree_cgroup_several(self, m_add, m_cre, m_path):
        gnodes = cgroupspy.nodes.NodeControlGroup("na")
        gnodes.nodes = [cgroupspy.nodes.Node,
                        cgroupspy.nodes.Node
                        ]
        m_path.side_effect = [gnodes]

        out = batch.create_tree_cgroups("66",
                                   self.parent_path,
                                   pid='19858'
                                   )
        self.assertIsNone(out)
        self.assertEqual(
            self.parent_path,
            m_path.call_args_list[0][0][0]
        )
        self.assertEqual(2, m_add.call_count)

    @mock.patch.object(cgroupspy.trees.GroupedTree, "get_node_by_path")
    @mock.patch.object(cgroupspy.nodes.Node, "create_cgroup")
    @mock.patch("bdocker.common.modules.batch.task_to_cgroup")
    def test_create_tree_cgroup_exception(self, m_add, m_cre, m_path):
        gnodes = cgroupspy.nodes.NodeControlGroup("na")
        gnodes.nodes = [cgroupspy.nodes.Node]
        m_path.side_effect = [gnodes,
                              ]
        m_cre.side_effect = exceptions.OSError(13, "err", "file")

        self.assertRaises(bdocker_exceptions.DockerException,
                          batch.create_tree_cgroups,
                          "66",
                          self.parent_path,
                          pid='19858',
                          )

    @mock.patch.object(cgroupspy.trees.GroupedTree,"get_node_by_path")
    @mock.patch.object(cgroupspy.nodes.Node,"delete_cgroup")
    @mock.patch("bdocker.common.modules.batch.task_to_cgroup")
    @mock.patch("bdocker.common.utils.read_file")
    def test_delete_tree_cgroup(self, m_rad, m_task, m_del, m_path):
        gnodes = cgroupspy.nodes.NodeControlGroup("na")
        parent_node = cgroupspy.nodes.Node("parent")
        gnodes.nodes = [cgroupspy.nodes.Node("", parent=parent_node)]
        m_path.side_effect = [gnodes]
        name = uuid.uuid4().hex
        out = batch.delete_tree_cgroups(name,
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

    @mock.patch.object(cgroupspy.trees.GroupedTree,"get_node_by_path")
    @mock.patch.object(cgroupspy.nodes.Node,"delete_cgroup")
    @mock.patch("bdocker.common.modules.batch.task_to_cgroup")
    @mock.patch("bdocker.common.utils.read_file")
    def test_delete_tree_cgroup_several_nodes(self, m_rad, m_task, m_del, m_path):
        gnodes = cgroupspy.nodes.NodeControlGroup("na")
        parent_node = cgroupspy.nodes.Node("parent")
        gnodes.nodes = [cgroupspy.nodes.Node("", parent=parent_node),
                        cgroupspy.nodes.Node("", parent=parent_node)]
        m_path.side_effect = [gnodes,
                              ]
        name = uuid.uuid4().hex
        out = batch.delete_tree_cgroups(name,
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

    @mock.patch("bdocker.common.utils.read_file")
    @mock.patch("bdocker.common.modules.batch.create_tree_cgroups")
    def test_conf_environment(self, m_cre, m_read):
        job_id = uuid.uuid4().hex
        spool_dir = "/foo"
        parent_id = uuid.uuid4().hex
        parent_dir = "/bdocker.test"
        conf = {"cgroups_dir": "/foo",
                "enable_cgroups": True,
                "parent_cgroup": parent_dir}
        m_read.return_value = parent_id
        controller = batch.SGEController(conf)
        cgroup = controller.conf_environment(job_id, spool_dir)
        expected_cgroup = "%s/%s" % (parent_dir, job_id)
        self.assertEqual(expected_cgroup, cgroup)
        self.assertIs(True, m_read.called)
        self.assertIs(True, m_cre.called)
        m_cre.assert_called_with(
            job_id,
            conf["parent_cgroup"],
            root_parent=conf["cgroups_dir"],
            pid=parent_id
        )

    @mock.patch("bdocker.common.utils.read_file")
    @mock.patch("bdocker.common.modules.batch.create_tree_cgroups")
    def test_conf_environment_no_root_dir(self, m_cre,  m_read):
        spool_dir = "/foo"
        job_id = uuid.uuid4().hex
        parent_id = uuid.uuid4().hex
        parent_dir = "/bdocker.test"
        conf = {
            "enable_cgroups": True,
            "parent_cgroup": parent_dir}
        m_read.return_value = parent_id
        controller = batch.SGEController(conf)
        cgroup = controller.conf_environment(job_id, spool_dir)
        expected_cgroup = "%s/%s" % (parent_dir, job_id)
        self.assertEqual(expected_cgroup, cgroup)
        self.assertIs(True, m_read.called)
        self.assertIs(True, m_cre.called)
        m_cre.assert_called_with(
            job_id,
            conf["parent_cgroup"],
            root_parent="/sys/fs/cgroup",
            pid=parent_id
        )

    @mock.patch("bdocker.common.utils.read_file")
    @mock.patch("bdocker.common.modules.batch.create_tree_cgroups")
    def test_conf_environment_no_cgroup(self, m_cre, m_read):
        spool_dir = "/foo"
        job_id = uuid.uuid4().hex
        parent_id = uuid.uuid4().hex
        conf = {"cgroups_dir": "/foo",
                "parent_cgroup": "/bdocker.test"}
        m_read.return_value = parent_id
        controller = batch.SGEController(conf)
        cgroup = controller.conf_environment(job_id, spool_dir)
        self.assertIsNone(cgroup)
        self.assertIs(False, m_read.called)
        self.assertIs(False, m_cre.called)

    @mock.patch("bdocker.common.modules.batch.delete_tree_cgroups")
    def test_clean_environment(self, m_del):
        job_id = uuid.uuid4().hex
        conf = {"cgroups_dir": "/foo",
                "enable_cgroups": True,
                "parent_cgroup": "/bdocker.test"}
        controller = batch.SGEController(conf)
        controller.clean_environment(job_id,)
        self.assertIs(True, m_del.called)
        m_del.assert_called_with(
            job_id,
            conf["parent_cgroup"],
            root_parent=conf["cgroups_dir"]
        )

    @mock.patch("bdocker.common.modules.batch.delete_tree_cgroups")
    def test_clean_environment_no_cgroup(self, m_del):
        job_id = uuid.uuid4().hex
        conf = {"cgroups_dir": "/foo",
                "parent_cgroup": "/bdocker.test"}
        controller = batch.SGEController(conf)
        controller.clean_environment(job_id)
        self.assertIs(False, m_del.called)

    def test_get_job_info(self):
        job_id = uuid.uuid4().hex
        user = uuid.uuid4().hex
        spool_dir = "/foo"
        os.environ["JOB_ID"] = job_id
        home = os.getenv("HOME")
        os.environ["USER"] = user
        os.environ["SGE_JOB_SPOOL_DIR"] = spool_dir
        expected = {'home': home,
                    'job_id': job_id,
                    'user': user,
                    'spool': spool_dir,
                    }
        out = batch.SGEController({}).get_job_info()
        self.assertEqual(out, expected)

