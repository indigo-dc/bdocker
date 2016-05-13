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

import testtools

from bdocker.server import utils
from bdocker.common import exceptions


class TestConfiguration(testtools.TestCase):
    """Test Configuration on Loading."""

    def setUp(self):
        super(TestConfiguration, self).setUp()

    def test_load_config_file(self):
        conf = utils.load_configuration(
            '/home/jorge/Dropbox/INDIGO_DOCKER/'
            'bdocker/bdocker/tests/server/'
            'fake_configure_file.cfg')
        self.assertIsNotNone(conf)
        self.assertEqual(4, conf.items().__len__())

    def test_load_config_file_error(self):
        self.assertRaises(exceptions.ConfigurationException,
                          utils.load_configuration,
            '/home/jorge/Dropbox/INDIGO_DOCKER/'
            'bdocker/bdocker/tests/server/'
            'fake_configure_file_error.cfg')