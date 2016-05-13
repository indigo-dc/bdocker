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
import yaml
import os

from bdocker.common import exceptions



def validate_directory(dir_request, dir_user):
    real_path = os.path.realpath(dir_request)
    prefix = os.path.commonprefix([real_path, dir_user])
    if prefix != dir_user:
        raise exceptions.UserCredentialsException(
            "User does not have permissons for %s"
            % real_path
        )



def read_yaml_file(path):
    f = open(path, 'r')
    data = f.read()
    f.close()
    return yaml.load(data)


def write_yaml_file(path, data):
    #f = open(path, 'w')
    yaml.safe_dump(data, file(path,'w'), encoding='utf-8', allow_unicode=True)
    #f.close()