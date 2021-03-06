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

import logging

from bdocker import utils

DEFAULT_LOG_FILE = "/var/log/bdocker.log"


def configure_logging():
    log_level = None
    log_file = None
    try:
        out = utils.load_configuration_from_file()
        log_file = DEFAULT_LOG_FILE
        if "logging" in out["server"]:
            log_level = out["server"]['logging']
        if "logging_file" in out["server"]:
            log_file = out["server"]['logging_file']
    except BaseException:
        pass
    try:
        logging.basicConfig(format='%(asctime)s - %(name)s -'
                                   ' %(levelname)s - %(message)s',
                            level=log_level, filename=log_file)
    except BaseException:
        pass

configure_logging()

LOG = logging.getLogger(__name__)
# log_handler = logging.handlers.SysLogHandler(address=log_data['file'])
# LOG.addHandler(log_handler)
