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


from gunicorn.app import base
from gunicorn import six


class StandaloneApplication(base.BaseApplication):
    def __init__(self, app, options=None):
        self.options = options or {}
        self.application = app
        super(StandaloneApplication, self).__init__()

    def load_config(self):
        config = dict(
            [(key, value) for key, value in six.iteritems(self.options)
             if key in self.cfg.settings and value is not None])
        for key, value in six.iteritems(config):
            self.cfg.set(key.lower(), value)

    def load(self):
        return self.application
