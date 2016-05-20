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
import webob

from bdocker.client.controller import commands
from bdocker.client.controller import utils


class TestIntegration(testtools.TestCase):
    def setUp(self):
        super(TestIntegration, self).setUp()
        endpoint = "http://127.0.0.1:5001"
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
    def test_ps_real(self):
        token = "1866e0ca1ad44a55952029817c2a5345"
        all = False
        result = self.controller.container_list(token, all)
        self.assertEqual([], result)

    def test_ps_real_no_token(self):
        token = None
        all = False
        result = self.controller.container_list(token, all)
        self.assertEqual([], result)

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