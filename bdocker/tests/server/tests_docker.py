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
import docker
import mock
import testtools
import uuid

from bdocker.server import docker as control_docker
from bdocker.server.docker import parsers
from bdocker.common import exceptions
from bdocker.tests.server import fake_docker_outputs

container1 = {'Command': '/bin/sleep 30',
              'Created': 1412574844,
              'Id': '6e276c9e6e5759e12a6a9214efec6439f80b4f37618e1a6547f28a3da34db07a',
              'Image': 'busybox:buildroot-2014.02',
              'Names': ['/grave_mayer'],
              'Ports': [],
              'Status': 'Up 1 seconds'}

container2 = {'Command': 'whoami',
              'Created': 1412574844,
              'Id': '89034890sdfdjlksdf93k2390kldfjlsdf09w80349ijfalfjf0393iu4pofjl33',
              'Image': 'busybox:buildroot-2014.02',
              'Names': ['/grave_mayer'],
              'Ports': [],
              'Status': 'Up 1 seconds'}

container_real = [{'Status': 'Exited (0) 6 minutes ago',
               'Created': 1458231723,
               'Image': 'ubuntu', 'Labels': {},
               'Ports': [], 'Command': 'sleep 30',
               'Names': ['/nostalgic_noyce'],
               'Id': 'f20b77988e436da8645cde68208'
                     '00dc9ee3aabe1bd9d2dd5b061a3c853ad688b'},
              {'Status': 'Exited (0) 7 minutes ago',
               'Created': 1458231670, 'Image': 'ubuntu',
               'Labels': {}, 'Ports': [], 'Command': 'whoami',
               'Names': ['/tender_nobel'],
               'Id': '144a7e26743ed487217ae1494cac01197'
                     '245ef8e64669c666addd6a770639264'}]


def create_generator(json_data):
    for line in json_data:
        yield line


class FakeDocker(control_docker.DockerController):
    def __init__(self):
        super(FakeDocker,self).__init__()

    def pull_image(self, repo):
        return {
            "status": "Pulling image (latest) from busybox, endpoint: ...",
            "progressDetail": {},
            "id": "e72ac664f4f0"
        }

    def delete_container(self, container_id):
        return ""

    def list_containers(self, containers):
        return [container1, container2]

    def logs_container(self, container_id):
        return "generator or str (test command)"

    def logs_container(self, container_id):
        return "generator or str (test command)"


class TestDocker(testtools.TestCase):
    """Test Docker controller."""

    def setUp(self):
        super(TestDocker, self).setUp()
        url = 'localhost:2375'
        self.control = control_docker.DockerController(url)

    @mock.patch.object(docker.Client, 'pull')
    def test_pull(self, m):
        image = 'imageOK'
        m.return_value = create_generator(fake_docker_outputs.fake_pull[image])
        out = self.control.pull_image(image)
        self.assertIsNotNone(out)
        self.assertIn('image_id',out)
        self.assertIn('status',out)

    @mock.patch.object(docker.Client, 'pull')
    def test_pull_exist(self, m):
        image = 'imageExist'
        m.return_value = create_generator(fake_docker_outputs.fake_pull[image])
        out = self.control.pull_image(image)
        self.assertIsNotNone(out)

    @mock.patch.object(docker.Client, 'pull')
    def test_pull_error(self, m):
        image = 'imageError'
        m.return_value = create_generator(fake_docker_outputs.fake_pull[image])
        self.assertRaises(exceptions.DockerException, self.control.pull_image, image)

    @mock.patch.object(docker.Client, 'remove_image')
    def test_delete_image(self, m):
        image = 'f1e4b055fb65'
        m.return_value = None
        out = self.control.delete_image(image)
        self.assertIsNotNone(out)

    @mock.patch.object(docker.Client, 'inspect_container')
    def test_list_containers(self, m):
        m.return_value = fake_docker_outputs.fake_container_info
        containers = ['xxx','xxxx']
        out = self.control.list_containers(containers)
        self.assertIsNotNone(out)
        self.assertEqual(2, out.__len__())

    @mock.patch.object(docker.Client, 'logs')
    @mock.patch.object(docker.Client, 'create_container')
    @mock.patch.object(docker.Client, 'start')
    def test_run_containers(self, ms, mc, ml):
        mc.return_value = fake_docker_outputs.fake_create
        ms.return_value = None
        ml.return_value = fake_docker_outputs.fake_log
        image_id = uuid.uuid4()
        detach = False
        container_id = self.control.create_container(image_id=image_id, detach=detach, command='')
        self.control.start_container(container_id)
        out_put = self.control.logs_container(container_id)
        self.assertEqual(fake_docker_outputs.fake_create['Id'], container_id)
        self.assertIsNotNone(out_put)
        self.assertEqual(out_put, fake_docker_outputs.fake_log)



    def test_accouning_error(self):
        self.assertRaises(exceptions.DockerException, self.control.accounting_container, None)

#########
# REAL
#######

    # def test_pull_real(self):
    #     image = 'busyboxy'
    #     out = self.control.pull_image(image)
    #     self.assertIsNotNone(out)
    #
    # def test_log_container_real(self):
    #     container_id = '15e3b92d919f441719704fa1287ea73a35faf26533c32bf58f4f642e9aac1a91'
    #     out = self.control.logs_container(container_id)
    #     self.assertIsNotNone(out)
    #     self.assertEqual(2, out.__len__())
    #
    # def test_list_containers_real(self):
    #     containers =['b5f659fba626','f20b77988e43']
    #     out = self.control.list_containers(containers)
    #     self.assertIsNotNone(out)
    #     self.assertEqual(2, out.__len__())
    #
    # def test_run_container_real(self):
    #     image_id = 'c917d6497f55'
    #     script = './bdocker_script.sh'
    #     detach = True
    #     host_dir = "/root/docker_test/"
    #     docker_dir = "/tmp"
    #     run_out = self.control.run_container(image_id,
    #                                          detach=detach,
    #                                          command=script,
    #                                          working_dir=docker_dir,
    #                                          host_dir=host_dir,
    #                                          docker_dir=docker_dir)
    #     out = self.control.logs_container(run_out)
    #     self.assertIsNotNone(out)
    #     self.assertEqual(1, out.__len__())

