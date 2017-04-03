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
import datetime
import json
import re

from bdocker import exceptions


def parse_docker_log(gen_data):
    dict_data = []
    for line in gen_data:
        dict_data.append(line.strip())
    return dict_data


def parse_docker_generator(gen_data):
    out_data = []
    try:
        for row in gen_data:
            json_row = json.loads(row)
            if 'id' in json_row:
                message = "%s: %s" % (
                    json_row['id'],
                    json_row['status']
                )
            elif 'status' in json_row:
                message = json_row['status']
            else:
                message = json_row['error']
            out_data.append(message)
        return out_data
    except KeyError:
        raise exceptions.ParseException('Pull output error',
                                        code=406)


def parse_docker_generator1(gen_data, key='Status'):  # Apparently this one isn't used
    dict_data = []
    for line in gen_data:
        dict_data.append(line.strip())
    try:
        out = json.loads(dict_data[dict_data.__len__() - 1])
        if 'status' in out:
            info = out['status']
        elif 'errorDetail' in out:
            info = out['errorDetail']['message']
        else:
            raise exceptions.ParseException('Pull output error',
                                            406)
        results = json.loads("{\"%s\"}"
                             % info.replace(":", "\":\"", 1))
    except BaseException:
        raise exceptions.ParseException('Pull output error',
                                        code=406)
    if key in results:
        out['image_id'] = json.loads(dict_data[2])['id']
        out['status'] = results[key]
        return out
    else:
        raise exceptions.ParseException(results['Error'],
                                        code=404)


def get_date_diff(date_end, date_format=None):
    if date_format:
        date_ini = datetime.datetime.strptime(date_end, date_format)
    else:
        date_ini = datetime.datetime.fromtimestamp(date_end)
    date_end = datetime.datetime.utcnow()
    difference = date_end - date_ini
    days = difference.days
    seconds = difference.seconds
    weeks = divmod(days, 7)[0]
    minutes = divmod(seconds, 60)[0]
    hours = divmod(seconds, 3600)[0]
    if weeks > 0:
        return "%s weeks ago" % weeks
    if days > 0:
        return "%s days ago" % days
    if hours > 0:
        return "%s hours ago" % hours
    if minutes > 0:
        return "%s minutes ago" % minutes
    return "%s seconds ago" % seconds


def parse_list_container_details(data):
    try:
        finish = get_date_diff(
            data['State']['FinishedAt'][:-4],
            "%Y-%m-%dT%H:%M:%S.%f"
        )
        created = get_date_diff(
            data['Created'][:-4],
            "%Y-%m-%dT%H:%M:%S.%f"
        )
        exit_data = "Excited (%s) %s" % (
            data['State']['ExitCode'],
            finish,
        )
        commands = ""
        for i in data['Config']['Cmd']:
            commands = "%s %s" % (commands, i)
        dict_data = [
            data['Config']['Hostname'],
            data['Config']['Image'],
            commands,
            created,
            exit_data,
            data['NetworkSettings']['Ports'],
            data['Name']
        ]
        #         dict_data = {
        #     'CONTAINER_ID': data['Config']['Hostname'],
        #     'IMAGE': data['Config']['Image'],
        #     'COMMANDS': commands,
        #     'CREATED': created,
        #     'STATUS': exit_data,
        #     'PORTS': data['NetworkSettings']['Ports'],
        #     'NAMES': data['Name']
        # }

    except BaseException:
        raise exceptions.ParseException('Container information error',
                                        code=406)
    return dict_data


def parse_list_container(data):
    try:
        created = get_date_diff(
            data['Created']
        )
        names = ""
        for i in data['Names']:
            name = re.sub('/', '', str(i))
            names = "%s %s" % (names, name)
        ports = ""
        for i in data['Ports']:
            ports = "%s %s" % (ports, str(i))
        out = [
            str(data['Id']),
            str(data['Image']),
            str(data['Command']),
            str(created),
            str(data['Status']),
            ports,
            names
        ]
    except BaseException:
        raise exceptions.ParseException(
            'Container information error',
            code=406
        )
    return out


def parse_inspect_container(data):
    json_data = json.dumps([data], indent=2)
    return json_data


def parse_time_to_nanoseconds(time_str):
    try:
        parsed = time_str.split(":")
        time_struc = datetime.timedelta(
            hours=int(parsed[0]),
            minutes=int(parsed[1]),
            seconds=int(parsed[2]))
        nanoseg = time_struc.total_seconds() * 1000000000
        return nanoseg
    except BaseException:
        return None
