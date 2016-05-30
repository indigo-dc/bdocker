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

from bdocker.common.modules import batch



class TestSGEController(testtools.TestCase):
    """Test SGE Batch controller."""
    def setUp(self):
        super(TestSGEController, self).setUp()
        self.control = batch.SGEController('/systemd/user/')

    def test_create_cgroup(self):
        out = self.control._create_cgroup("test_group")
        self.assertIsNone(out)

    def test_delete_cgroup(self):
        out = self.control._delete_cgroup("test_group")
        self.assertIsNone(out)

if __name__ == '__main__':
    testtools.sys.argv.insert(1,'--verbose')
    testtools.main(argv = testtools.sys.argv)