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


from bdocker.client.controller import commands
from bdocker.client.controller import utils


class TestIntegration(testtools.TestCase):
    def setUp(self):
        super(TestIntegration, self).setUp()
        endpoint = "http://localhost:5001"
        os.environ['BDOCKER_CONF_FILE'] = "/home/jorge/Dropbox/INDIGO_DOCKER/bdocker/bdocker/common/configure_bdocker.cfg"
        os.environ['JOB_ID'] = 'None'
        self.controller = commands.CommandController(endpoint=endpoint)

#     def create_request(self, path="/",
#                        **kwargs):
#         return webob.Request.blank(path=path, **kwargs)
#
# class TestRESTIntegration(TestIntegration):
#     """Test REST request mapping."""
#
#     def setUp(self):
#         super(TestRESTIntegration, self).setUp()

    #

    # def test_clean(self):
    #     token = "22e441824ca64523a7c75fcbf4779287"
    #     result = self.controller.clean_environment(None)
    #     self.assertEqual(token, result)

    def test_ps_real(self):
        token = "b633b5a7c2f545de9bec6db41b8c831d"
        all = False
        result = self.controller.container_list(token, all)
        self.assertEqual([], result)

    def test_ps_real_no_token(self):
        token = None
        all = True
        result = self.controller.container_list(token, all)
        self.assertNotEqual([], result)

    def test_delete_real_no_token(self):
        token = None
        all = True
        result = self.controller.container_delete(token, all)
        self.assertNotEqual([], result)

    def test_ps_run(self):
        token = None # "1866e0ca1ad44a55952029817c2a5345"
        all = False
        image_id = "a83540abf000"
        detach = False
        script = './hostname.sh'
        workdir='/tmp'
        volume={"host_dir": "/home/jorgesece/docker_test/",
               "docker_dir": "/tmp"
        }
        os.environ['BDOCKER_TOKEN_FILE'] = '/home/jorge/.bdocker_token'
        try:
            result = self.controller.container_run(
                token, image_id, detach, script,
                workdir,
                volume
            )
        except BaseException as e:
            utils.print_error(e.message)
        result = self.controller.container_list(token, all)
        self.assertEqual([], result)

    # def test_logs_real(self):
    #     token = "f055450bf8c94390b12388cd06e60a56"
    #     container_id = '88'
    #     result = self.controller.container_logs(token, container_id)
    #     self.assertEqual([], result)