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

import testtools
import ConfigParser
import StringIO

from bdocker import utils
from bdocker import exceptions


class TestConfigurationWorkingNode(testtools.TestCase):
    """Test Configuration on Loading."""

    def setUp(self):
        super(TestConfigurationWorkingNode, self).setUp()

    def test_load_config_file(self):
        conf = utils.load_configuration_from_file(
            '/home/jorge/Dropbox/INDIGO_DOCKER/'
            'bdocker/bdocker/tests/modules/'
            'fake_configure_file.cfg')
        self.assertIsNotNone(conf)
        self.assertEqual(6, conf.items().__len__())

    def test_load_config_file_error(self):
        self.assertRaises(exceptions.ConfigurationException,
                          utils.load_configuration_from_file,
            '/home/jorge/Dropbox/INDIGO_DOCKER/'
            'bdocker/bdocker/tests/modules/'
            'fake_configure_file_error.cfg')


class TestConfigurationMaster(testtools.TestCase):
    """Test Configuration on Loading."""

    def setUp(self):
        super(TestConfigurationMaster, self).setUp()

    def test_load_config_file(self):
        conf = utils.load_configuration_from_file(
            '/home/jorge/Dropbox/INDIGO_DOCKER/'
            'bdocker/bdocker/tests/modules/'
            'fake_configure_file_accounting.cfg')
        self.assertIsNotNone(conf)
        self.assertEqual(4, conf.items().__len__())

    def test_load_config_file_error(self):
        self.assertRaises(exceptions.ConfigurationException,
                          utils.load_configuration_from_file,
            '/home/jorge/Dropbox/INDIGO_DOCKER/'
            'bdocker/bdocker/tests/modules/'
            'fake_configure_file_error.cfg')

    def test_load_config_file2(self):
        path = (
            '/home/jorge/Dropbox/INDIGO_DOCKER/bdocker/'
            'bdocker/tests/spool_config')
        config_dict = utils.load_sge_job_configuration(path)
        self.assertIsNotNone(config_dict)