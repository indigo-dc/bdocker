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

import copy
import os

import testtools

from bdocker import exceptions
from bdocker import utils
from bdocker.tests import fakes


class TestConfigurationWorkingNode(testtools.TestCase):
    """Test Configuration on Loading."""

    def setUp(self):
        super(TestConfigurationWorkingNode, self).setUp()

    def test_load_config_file(self):
        file_name = os.path.join(os.path.dirname(__file__),
                                 'fake_configure_file.cfg')
        conf = utils.load_configuration_from_file(file_name)
        self.assertIsNotNone(conf)
        self.assertEqual(6, conf.items().__len__())

    def test_load_config_file_error(self):
        file_name = os.path.join(os.path.dirname(__file__),
                                 'fake_configure_file_error.cfg')
        self.assertRaises(exceptions.ConfigurationException,
                          utils.load_configuration_from_file,
                          file_name
                          )

    def test_validation(self):
        out = utils.validate_config(fakes.conf_sge)
        self.assertIsNone(out)

    def test_validation_error_resource(self):
        conf = copy.deepcopy(fakes.conf_sge)
        conf.pop('resource')
        self.assertRaises(exceptions.ParseException,
                          utils.validate_config, conf)

    def test_validation_error_role(self):
        conf = copy.deepcopy(fakes.conf_sge)
        right_roles = {'working', 'accounting'}
        for r in right_roles:
            conf["resource"]["role"] = r
            utils.validate_config(conf)
        conf["resource"]["role"] = "err"
        self.assertRaises(exceptions.ParseException,
                          utils.validate_config, conf)

    def test_validation_error_accounting_server(self):
        conf = copy.deepcopy(fakes.conf_sge)
        conf.pop('accounting_server')
        self.assertRaises(exceptions.ParseException,
                          utils.validate_config, conf)

    def test_validation_error_acc_error(self):
        conf = copy.deepcopy(fakes.conf_sge)
        conf["accounting_server"].pop("host")
        self.assertRaises(exceptions.ParseException,
                          utils.validate_config, conf)

    def test_validation_error_credentials(self):
        conf = copy.deepcopy(fakes.conf_sge)
        conf.pop('credentials')
        self.assertRaises(exceptions.ParseException,
                          utils.validate_config, conf)

    def test_validation_error_token_store(self):
        conf = copy.deepcopy(fakes.conf_sge)
        conf["credentials"].pop("token_store")
        self.assertRaises(exceptions.ParseException,
                          utils.validate_config, conf)

    def test_validation_error_docker(self):
        conf = copy.deepcopy(fakes.conf_sge)
        conf.pop('dockerAPI')
        self.assertRaises(exceptions.ParseException,
                          utils.validate_config, conf)

    def test_validation_error_base_url(self):
        conf = copy.deepcopy(fakes.conf_sge)
        conf["dockerAPI"].pop("base_url")
        self.assertRaises(exceptions.ParseException,
                          utils.validate_config, conf)

    def test_validation_error_server(self):
        conf = copy.deepcopy(fakes.conf_sge)
        conf.pop('server')
        self.assertRaises(exceptions.ParseException,
                          utils.validate_config, conf)

    def test_validation_error_host(self):
        conf = copy.deepcopy(fakes.conf_sge)
        conf["server"].pop("host")
        self.assertRaises(exceptions.ParseException,
                          utils.validate_config, conf)

    def test_validation_error_port(self):
        conf = copy.deepcopy(fakes.conf_sge)
        conf["server"].pop("port")
        self.assertRaises(exceptions.ParseException,
                          utils.validate_config, conf)

    def test_validation_error_logging(self):
        conf = copy.deepcopy(fakes.conf_sge)
        right_values = {'ERROR', 'WARNING', 'INFO', 'DEBUG'}
        for r in right_values:
            conf["server"]["logging"] = r
            utils.validate_config(conf)
        conf["server"]["logging"] = "err"
        self.assertRaises(exceptions.ParseException,
                          utils.validate_config, conf)
        conf["server"].pop("logging")
        utils.validate_config(conf)

    def test_validation_error_batch(self):
        conf = copy.deepcopy(fakes.conf_sge)
        conf.pop('batch')
        self.assertRaises(exceptions.ParseException,
                          utils.validate_config, conf)

    def test_validation_error_batch_system(self):
        conf = copy.deepcopy(fakes.conf_sge)
        conf["batch"].pop("system")
        self.assertRaises(exceptions.ParseException,
                          utils.validate_config, conf)


class TestConfigurationMaster(testtools.TestCase):
    """Test Configuration on Loading."""

    def setUp(self):
        super(TestConfigurationMaster, self).setUp()

    def test_load_config_file(self):
        file_name = os.path.join(os.path.dirname(__file__),
                                 'fake_configure_file_accounting.cfg')
        conf = utils.load_configuration_from_file(file_name)
        self.assertIsNotNone(conf)
        self.assertEqual(4, conf.items().__len__())

    def test_load_config_file_error(self):
        file_name = os.path.join(os.path.dirname(__file__),
                                 'fake_configure_file_error.cfg')
        self.assertRaises(exceptions.ConfigurationException,
                          utils.load_configuration_from_file,
                          file_name)

    def test_load_sge_job_config(self):
        file_name = os.path.join(os.path.dirname(__file__),
                                 'sge_spool_config')
        config_dict = utils.load_sge_job_configuration(file_name)
        self.assertIsNotNone(config_dict)

    def test_validation(self):
        conf = copy.deepcopy(fakes.conf_sge)
        conf["resource"]["role"] = "accounting"
        out = utils.validate_config(fakes.conf_sge)
        self.assertIsNone(out)

    def test_validation_no_error_docker(self):
        conf = copy.deepcopy(fakes.conf_sge)
        conf["resource"]["role"] = "accounting"
        conf.pop('dockerAPI')
        out = utils.validate_config(conf)
        self.assertIsNone(out)

    def test_validation_error_accounting_server(self):
        conf = copy.deepcopy(fakes.conf_sge)
        conf["resource"]["role"] = "accounting"
        conf.pop('accounting_server')
        out = utils.validate_config(conf)
        self.assertIsNone(out)