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
import json
import uuid

import docker
import mock
import testtools

from bdocker import exceptions
from bdocker.modules import docker_helper
from bdocker.tests.modules import fake_docker_outputs


def create_generator(json_data):
    for line in json_data:
        yield line


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
        m.return_value = create_generator(
            fake_docker_outputs.fake_pull[image]
        )
        self.assertRaises(exceptions.DockerException,
                          self.control.pull_image, image)

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
    def test_clean_containers_not_found(self, m):
        m.side_effect = exceptions.DockerException(
            code=204,
            message="Not Found"
        )
        c_1 = uuid.uuid4().hex
        self.assertRaises(exceptions.DockerException,
                          self.control.list_containers_details,
                          c_1)

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
        container_id = self.control.run_container(
            image_id=image_id, detach=detach, command='')
        self.control.start_container(container_id)
        out_put = self.control.logs_container(container_id)
        self.assertEqual(fake_docker_outputs.fake_create['Id'],
                         container_id)
        self.assertIsNotNone(out_put)
        self.assertEqual(out_put, fake_docker_outputs.fake_log)

    @mock.patch.object(docker.Client, 'inspect_container')
    @mock.patch("bdocker.parsers.parse_inspect_container")
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
    @mock.patch("bdocker.parsers.parse_inspect_container")
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
    @mock.patch("bdocker.parsers.parse_docker_log")
    def test_logs(self, m_parse, m_log):
        logs = fake_docker_outputs.fake_log
        m_parse.return_value = logs
        m_log.return_value = fake_docker_outputs.create_generator(logs)
        container_id = uuid.uuid4().hex
        out = self.control.logs_container(container_id)
        self.assertIsNotNone(out)
        self.assertEqual(logs, out)

    @mock.patch.object(docker.Client, 'logs')
    @mock.patch("bdocker.parsers.parse_docker_log")
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

    @mock.patch.object(docker.Client, 'get_archive')
    @mock.patch("io.FileIO")
    @mock.patch("tarfile.TarInfo")
    @mock.patch("tarfile.TarFile")
    def test_copy_from_container(self, m_tar, m_tarinf, m_file, m_get):
        docker_out = mock.MagicMock()
        stat = {}
        m_get.return_value = docker_out, stat
        container_id = uuid.uuid4().hex
        container_path = "/baa"
        host_path = "/foo"
        out = self.control.copy_from_container(container_id,
                                               container_path,
                                               host_path)
        self.assertEqual(stat, out)

    @mock.patch.object(docker.Client, 'put_archive')
    @mock.patch("io.FileIO")
    @mock.patch("tarfile.TarFile")
    @mock.patch("os.path")
    def test_copy_to_container(self, m_os, m_tar, m_file, mput):
        mput.return_value = True
        container_id = uuid.uuid4().hex
        container_path = "/baa"
        host_path = "/foo"
        out = self.control.copy_to_container(container_id,
                                             container_path,
                                             host_path)
        self.assertEqual(True, out)
