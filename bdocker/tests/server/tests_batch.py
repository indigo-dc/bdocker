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
import os
import testtools
import uuid

from bdocker.common.modules import batch


class TestSGEController(testtools.TestCase):
    """Test SGE Batch controller."""
    def setUp(self):
        super(TestSGEController, self).setUp()
        self.parent_path = "/systemd/user/"
        #

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
    @mock.patch("bdocker.common.modules.batch.create_cgroups")
    def test_conf_environment(self, m_cre, m_read):
        job_id = uuid.uuid4().hex
        spool_dir = "/foo"
        parent_id = uuid.uuid4().hex
        conf = {"cgroups_dir": "/foo",
                "cgroups": ['cpu', 'memmory']}
        m_read.return_value = parent_id
        controller = batch.SGEController(conf)
        controller.conf_environment(job_id, spool_dir)
        self.assertIs(True, m_read.called)
        self.assertIs(True, m_cre.called)
        m_cre.assert_called_with(
            job_id,
            conf["cgroups"],
            root_parent=conf["cgroups_dir"],
            pid=parent_id
        )

    @mock.patch("bdocker.common.utils.read_file")
    @mock.patch("bdocker.common.modules.batch.create_cgroups")
    def test_conf_environment_no_root_dir(self, m_cre, m_read):
        spool_dir = "/foo"
        job_id = uuid.uuid4().hex
        parent_id = uuid.uuid4().hex
        conf = {
            "cgroups": ['cpu', 'memmory']}
        m_read.return_value = parent_id
        controller = batch.SGEController(conf)
        controller.conf_environment(job_id, spool_dir)
        self.assertIs(True, m_read.called)
        self.assertIs(True, m_cre.called)
        m_cre.assert_called_with(
            job_id,
            conf["cgroups"],
            root_parent="/sys/fs/cgroup",
            pid=parent_id
        )

    @mock.patch("bdocker.common.utils.read_file")
    @mock.patch("bdocker.common.modules.batch.create_cgroups")
    def test_conf_environment_no_cgroup(self, m_cre, m_read):
        spool_dir = "/foo"
        job_id = uuid.uuid4().hex
        parent_id = uuid.uuid4().hex
        conf = {"cgroups_dir": "/foo"}
        m_read.return_value = parent_id
        controller = batch.SGEController(conf)
        controller.conf_environment(job_id, spool_dir)
        self.assertIs(False, m_read.called)
        self.assertIs(False, m_cre.called)

    @mock.patch("bdocker.common.modules.batch.delete_cgroups")
    def test_clean_environment(self, m_del):
        job_id = uuid.uuid4().hex
        conf = {"cgroups_dir": "/foo",
                "cgroups": ['cpu', 'memmory']}
        controller = batch.SGEController(conf)
        controller.clean_environment(job_id)
        self.assertIs(True, m_del.called)
        m_del.assert_called_with(
            job_id,
            conf["cgroups"],
            root_parent=conf["cgroups_dir"]
        )

    @mock.patch("bdocker.common.modules.batch.delete_cgroups")
    def test_clean_environment_no_cgroup(self, m_del):
        job_id = uuid.uuid4().hex
        conf = {"cgroups_dir": "/foo"}
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
                    'spool': spool_dir
                    }
        out = batch.SGEController({}).get_job_info()
        self.assertEqual(out, expected)
