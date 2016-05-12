# -*- coding: utf-8 -*-

# Copyright 2016 LIP - Lisbon
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

from bdocker.client.controller import utils
from bdocker.common import exceptions
from bdocker.common import utils as utils_common
from bdocker.server import parsers

class TestParsers(testtools.TestCase):
    """Test User Parsers."""

    def setUp(self):
        super(TestParsers, self).setUp()

    def test_date_diff_minutes(self):
        d = '2016-05-10T15:34:15.408295804Z'
        result = parsers.get_date_diff(d[:-4], "%Y-%m-%dT%H:%M:%S.%f")
        self.assertIsNotNone(result)


    # def test_print_table(self):
    #     out = []
    #     out.append(["HEADER1", "HEADER2", "HEADER3"])
    #     out.append([1, 1, 1])
    #     out.append([2, 2, 2])
    #     utils.print_table(out.pop(0), out)

    def test_parse_vol(self):
        h_dir = "/root/docker_test/"
        d_dir = "/tmp"
        volume_path = "%s:%s" % (h_dir, d_dir)
        vol = utils.parse_volume(None, None, volume_path)
        self.assertEqual(h_dir, vol['host_dir'])
        self.assertEqual(d_dir, vol['docker_dir'])

    def test_parse_vol_empty(self):
        volume_path = None
        vol = utils.parse_volume(None, None, volume_path)
        self.assertIsNone(vol)

    def test_validate_dir(self):
        home_path = '/home/jorge'
        req_path = '%s/nuevo/script_dir' % home_path

        result = utils_common.validate_directory(req_path, home_path)
        self.assertIsNone(result)

    def test_validate_dir_invalid(self):
        home_path = '/home/jorge'
        req_path = '/root/nuevo/script_dir'

        self.assertRaises(exceptions.UserCredentialsException,
                          utils_common.validate_directory,
                          req_path, home_path)

