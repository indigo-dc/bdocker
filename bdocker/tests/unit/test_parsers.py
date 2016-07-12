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

from bdocker import exceptions
from bdocker import parsers
from bdocker.tests import fakes
from bdocker import utils


class TestParsers(testtools.TestCase):
    """Test Parsers."""

    def setUp(self):
        super(TestParsers, self).setUp()

    def test_date_diff_minutes(self):
        d = '2016-05-10T15:34:15.408295804Z'
        result = parsers.get_date_diff(d[:-4], "%Y-%m-%dT%H:%M:%S.%f")
        self.assertIsNotNone(result)

    def test_validate_dir(self):
        home_path = '/home/jorge'
        req_path = '%s/nuevo/script_dir' % home_path

        result = utils.validate_directory(req_path, home_path)
        self.assertIsNone(result)

    def test_validate_dir_invalid(self):
        home_path = '/home/jorge'
        req_path = '/root/nuevo/script_dir'

        self.assertRaises(exceptions.UserCredentialsException,
                          utils.validate_directory,
                          req_path, home_path)

    def test_logs(self):
        log_list = fakes.fake_log
        log_gen = fakes.create_generator(log_list)
        out = parsers.parse_docker_log(log_gen)
        self.assertIsNotNone(out)
        self.assertEqual(log_list, out)

    def test_details(self):
        details = fakes.fake_container_details
        out = parsers.parse_inspect_container(details)
        self.assertIsNotNone(out)

    def test_parse_hours(self):
        hour = 55
        minute = 0
        second = 1
        fact = 1000000000
        nanosenconds = (hour * 60 * 60 + minute * 60 + second) * fact
        time_str = "%s:%s:%s" % (hour, minute, second)
        out = parsers.parse_time_to_nanoseconds(time_str)
        self.assertIsNotNone(out)
        self.assertEqual(nanosenconds, out)

    def test_parse_hours_none(self):
        out = parsers.parse_time_to_nanoseconds(None)
        self.assertIsNone(out)
