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

import json

from bdocker.common import exceptions


def parse_docker_log(gen_data):
    dict_data = []
    for line in gen_data:
        dict_data.append(line.strip())
    return dict_data


def parse_docker_generator(gen_data, key='Status'):
    dict_data = []
    for line in gen_data:
        dict_data.append(line.strip())
    try:
        out = json.loads(dict_data[dict_data.__len__()-1])
        if 'status' in out:
            info = out['status']
        elif 'errorDetail' in out:
            info = out['errorDetail']['message']
        else:
            raise exceptions.ParseException('Pull output error',
                                            406)
        results = json.loads("{\"%s\"}"
                                 % info.replace(":", "\":\"", 1))
    except BaseException as e:
        raise exceptions.ParseException('Pull output error',
                                        code=406)
    if key in results:
        out['image_id'] = json.loads(dict_data[2])['id']
        out['status'] = results[key]
        return out
    else:
        raise exceptions.ParseException(results['Error'],
                                        code=404)


def parse_list_container(data):
    try:
        dict_data = { 'exit': data['State']['ExitCode'],
                      'image': data['Config']['Image'],
                      'container': data['Config']['Hostname'],
                      'command': data['Config']['Cmd'],
                      'created': data['Created'],
                      'name': data['Name']
                      }
    except BaseException as e:
        raise exceptions.ParseException('Container information error',
                                        code=406)
    return dict_data
