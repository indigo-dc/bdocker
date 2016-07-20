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

# import logging.handlers
#
# my_logger = logging.getLogger('MyLogger')
# my_logger.setLevel(logging.DEBUG)
#
# handler = logging.handlers.SysLogHandler(address = '/dev/log')
#
# my_logger.addHandler(handler)


def log_level():
    try:
        out = utils.load_configuration_from_file()
        return out["server"]['logging']
    except BaseException:
        return None


logging.basicConfig(format='%(asctime)s - %(name)s -'
                           ' %(levelname)s - %(message)s',
                    level=log_level())
LOG = logging.getLogger(__name__)
