# -*- coding: utf-8 -*-

# Copyright 2015 LIP - INDIGODataCLOUD
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

from bdocker.api import working_node
from bdocker import middleware

if __name__ == '__main__':
    conf = working_node.load_configuration()
    port = conf['server']['port']
    host = conf['server']['host']
    workers = conf["server"].get("workers", 2)
    time_out = conf["server"].get("timeout", 200)
    options = {
        'bind': '%s:%s' % (host, port),
        'workers': workers,
        'timeout': time_out
    }
    middleware.StandaloneApplication(working_node.app, options).run()
