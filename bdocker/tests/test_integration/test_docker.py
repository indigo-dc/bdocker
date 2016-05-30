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
import os
import testtools

from bdocker.common.modules import docker_helper


class TestDockerIntegration(testtools.TestCase):
    def setUp(self):
        super(TestDockerIntegration, self).setUp()
        url = 'localhost:2375'
        self.control = docker_helper.DockerController(url)

    def test_ps_real(self):
        token = "1866e0ca1ad44a55952029817c2a5345"
        all = False
        result = self.control.list_containers(token, all)
        self.assertEqual([], result)

     # def test_pull_real(self):
    #     image = 'ubuntu'
    #     out = self.control.pull_image(image)
    #     self.assertIsNotNone(out)

    # def test_log_container_real(self):3413
    #     container_id = '15e3b92d919f441719704fa1287ea73a35faf26533c32bf58f4f642e9aac1a91
    #     out = self.control.logs_container(container_id)
    #     self.assertIsNotNone(out)
    #     self.assertEqual(2, out.__len__())
    #
    # def test_list_containers_real(self):
    #     containers =['b5f659fba626','f20b77988e43']
    #     out = self.control.list_containers(containers, all=False)
    #     self.assertIsNotNone(out)
    #     self.assertEqual(2, out.__len__())
    #
    def test_run_container_real(self):
        image_id = 'a83540abf000'
        script = 'sleep 360'
        detach = True
        host_dir = "/root/docker_test/"
        docker_dir = "/tmp"
        container_id = self.control.run_container(image_id,
                                             detach=detach,
                                             command=script,
                                             working_dir=docker_dir,
                                             host_dir=host_dir,
                                             docker_dir=docker_dir)

        outstart = self.control.start_container(container_id)
        details = self.control.container_details(container_id)
        out = self.control.logs_container(container_id)
        self.assertIsNotNone(out)
        self.assertIsNotNone(out.__len__())
    #
    # def test_run_container_real_ls(self):
    #     image_id = 'a83540abf000'
    #     script = 'ls'
    #     detach = True
    #     host_dir = None #"/root/docker_test/"
    #     docker_dir = None # "/tmp"
    #     container_id = self.control.run_container(image_id,
    #                                          detach=detach,
    #                                          command=script,
    #                                          working_dir=docker_dir,
    #                                          host_dir=host_dir,
    #                                          docker_dir=docker_dir)
    #     self.control.start_container(container_id)
    #     out = self.control.logs_container(container_id)
    #     self.assertIsNotNone(out)
    #     self.assertEqual(1, out.__len__())
