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


def parse_docker_generator(gen_data, key='Status'):
    dict_data = []
    for line in gen_data:
        dict_data.append(line.strip())
    out = json.loads(dict_data[dict_data.__len__()-1])
    try:
        results = json.loads("{\"%s\"}"
                             % out['status'].replace(":", "\":\"",1))
    except BaseException as e:
        raise exceptions.ParseException('Pull output error',
                                        code=406)
    if key in results:
        return results[key]
    else:
        raise exceptions.ParseException(results['Error'],
                                        code=404)