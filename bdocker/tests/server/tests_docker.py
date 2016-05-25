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
import json
import uuid

import docker
import mock
import testtools

from bdocker.common import exceptions
from bdocker.common.modules import docker_helper
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


class FakeDocker(docker_helper.DockerController):
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
        self.control = docker_helper.DockerController(url)

    @mock.patch.object(docker.Client, 'pull')
    def test_pull(self, m):
        image = 'imageOK'
        m.return_value = create_generator(fake_docker_outputs.fake_pull[image])
        out = self.control.pull_image(image)
        self.assertIsNotNone(out)

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
        image = uuid.uuid4().hex
        m.return_value = None
        out = self.control.delete_image(image)
        self.assertIsNone(out)

    @mock.patch.object(docker.Client, 'remove_container')
    def test_delete_container(self, m):
        container_id = uuid.uuid4().hex
        m.return_value = None
        out = self.control.delete_container(container_id)
        self.assertEqual(container_id, out)

    @mock.patch.object(docker.Client, 'remove_container')
    def test_clean_containers(self, m):
        m.side_effect = exceptions.DockerException(
            code=204,
            message="Not Found"
        )
        c_1 = uuid.uuid4().hex
        out = self.control.delete_container(c_1)
        self.assertEqual([], out)


    @mock.patch.object(docker.Client, 'remove_container')
    def test_clean_several_containers(self, m):
        c_1 = uuid.uuid4().hex
        c_2 = uuid.uuid4().hex
        containers = [c_1, c_2]
        m.side_effect = {c_1, c_2}
        out = self.control.clean_containers(containers)
        self.assertEqual(containers.__len__(), out.__len__())

    @mock.patch.object(docker.Client, 'remove_container')
    def test_clean_containers(self, m):
        out = self.control.clean_containers(None)
        self.assertEqual([], out)

    @mock.patch.object(docker.Client, 'remove_container')
    def test_clean_containers_err(self, m):
        m.side_effect = exceptions.DockerException(
            code=204,
            message="Not Found"
        )
        c_1 = [uuid.uuid4().hex]
        out = self.control.clean_containers(c_1)
        self.assertIn('Error', out[0])

    @mock.patch.object(docker.Client, 'inspect_container')
    def test_list_containers_details(self, m):
        m.return_value = fake_docker_outputs.fake_container_details
        containers = [uuid.uuid4().hex, uuid.uuid4().hex]
        out = self.control.list_containers_details(containers)
        self.assertIsNotNone(out)
        self.assertEqual(2, out.__len__())

    def test_list_containers_details_empty(self):
        out = self.control.list_containers_details([])
        self.assertIsNotNone(out)
        self.assertEqual(0, out.__len__())

    @mock.patch.object(docker.Client, 'inspect_container')
    def test_list_containers_details_err(self, m):
        m.side_effect = exceptions.DockerException(
            code=204,
            message="Not Found"
        )
        containers = [uuid.uuid4().hex, uuid.uuid4().hex]
        self.assertRaises(exceptions.DockerException,
                  self.control.list_containers_details,
                  containers[0])

    @mock.patch.object(docker.Client, 'containers')
    def test_list_containers(self, m):
        m.return_value = fake_docker_outputs.fake_container_info
        containers = fake_docker_outputs.fake_containers
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
        container_id = self.control.run_container(image_id=image_id, detach=detach, command='')
        self.control.start_container(container_id)
        out_put = self.control.logs_container(container_id)
        self.assertEqual(fake_docker_outputs.fake_create['Id'], container_id)
        self.assertIsNotNone(out_put)
        self.assertEqual(out_put, fake_docker_outputs.fake_log)

    @mock.patch.object(docker.Client, 'inspect_container')
    @mock.patch("bdocker.common.parsers.parse_inspect_container")
    def test_containers_details(self, m_parse, m_ins):
        details = fake_docker_outputs.fake_container_details
        m_parse.return_value = json.dumps(details)
        m_ins.return_value = fake_docker_outputs.create_generator(details)
        container_id = uuid.uuid4().hex
        out = self.control.container_details(container_id)
        self.assertIsNotNone(out)
        json_data = json.loads(out)
        self.assertIn("State", json_data)

    @mock.patch.object(docker.Client, 'inspect_container')
    @mock.patch("bdocker.common.parsers.parse_inspect_container")
    def test_containers_details_err(self, m_parse, m_ins):
        container_id = uuid.uuid4().hex
        m_ins.side_effect = exceptions.DockerException(
            code=204,
            message="Not Found"
        )
        self.assertRaises(exceptions.DockerException,
                  self.control.container_details,
                  container_id)

    @mock.patch.object(docker.Client, 'logs')
    @mock.patch("bdocker.common.parsers.parse_docker_log")
    def test_logs(self, m_parse, m_log):
        logs = fake_docker_outputs.fake_log
        m_parse.return_value = logs
        m_log.return_value = fake_docker_outputs.create_generator(logs)
        container_id = uuid.uuid4().hex
        out = self.control.logs_container(container_id)
        self.assertIsNotNone(out)
        self.assertEqual(logs, out)

    @mock.patch.object(docker.Client, 'logs')
    @mock.patch("bdocker.common.parsers.parse_docker_log")
    def test_logs_err(self, m_parse, m_log):
        container_id = uuid.uuid4().hex
        m_log.side_effect = exceptions.DockerException(
            code=204,
            message="Not Found"
        )
        self.assertRaises(exceptions.DockerException,
                  self.control.container_details,
                  container_id)

    @mock.patch.object(docker.Client, 'start')
    def test_start(self, m):
        m.return_value = None
        container_id = uuid.uuid4().hex
        out = self.control.start_container(container_id)
        self.assertIsNone(out)

    @mock.patch.object(docker.Client, 'start')
    def test_start_err(self, m):
        container_id = uuid.uuid4().hex
        m.side_effect = exceptions.DockerException(
            code=204,
            message="Not Found"
        )
        self.assertRaises(exceptions.DockerException,
                  self.control.start_container,
                  container_id)

# TODO(jorgesece): implement and test it

    def test_accouning_error(self):
        self.assertRaises(exceptions.DockerException, self.control.accounting_container, None)



