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
import testtools
import uuid

from bdocker.common import utils


class TestUtils(testtools.TestCase):
    """Test SGE Batch controller."""
    def setUp(self):
        super(TestUtils, self).setUp()

    def test_write_file(self):
        path = "/home/jorge/.bdocker_accounting_test"
        acc = {"write": "testing"}
        utils.write_yaml_file(path, acc)

    def test_update_file(self):
        path = "/home/jorge/.bdocker_accounting_test"
        acc = {"update": "testing"}
        i=0
        while i<3:
            utils.update_yaml_file(path, acc)
            i=i+1