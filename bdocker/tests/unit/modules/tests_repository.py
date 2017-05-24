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

import mock
import testtools

from bdocker.modules import repository
from bdocker.tests import fakes


class TestFileController(testtools.TestCase):

    def setUp(self):
        super(TestFileController, self).setUp()
        self.conf = {"location": "foo"}
        self.controller = repository.FileController(self.conf)

    @mock.patch("bdocker.utils.read_yaml_file")
    def test_pull(self, mock_read):
        mock_read.return_value = fakes.repository_content
        result = self.controller.get_image("ubuntu:indigo")
        file_expected = fakes.repository_content["ubuntu"]["indigo"]["file"]
        expected = "%s/%s" % (self.conf["location"], file_expected)
        self.assertEqual(expected, result)