# -*- coding: utf-8 -*-

# Copyright 2015 LIP - Lisbon
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
from tabulate import tabulate
import json
import pwd
import six

from bdocker.common import exceptions
from bdocker.common import utils


colors = {"WARNING": "\033[93m",
          'FAIL': '\033[91m'}


colors = { 'FAIL' : '\033[91m',
           'OK': '\033[92m',
           'WARNING': '\033[93m',
           'ENDC': '\033[0m'
         }

messages = { "empty": colors['FAIL'] + ' "Parsing error" ' + colors['ENDC'],
            "error": "There was an error"
          }


def utf8(value):
    """Try to turn a string into utf-8 if possible.

    Code is modified from the utf8 function in
    http://github.com/facebook/tornado/blob/master/tornado/escape.py

    """
    if isinstance(value, six.text_type):
        return value.encode('utf-8')
    assert isinstance(value, str)
    return value


def get_query_string(parameters):
        query_string = ""
        if parameters is None:
            return None

        for key in parameters.keys():
            query_string = ("%s%s=%s&" % (query_string, key, parameters[key]))

        return query_string[:-1] # delete last character


def make_body(parameters):
        body = {}
        for key in parameters.keys():
            body[key] = parameters[key]

        return json.dumps(body)


def get_user_credentials(uid):
    try:
        info = pwd.getpwuid(uid)
        user = {'uid': uid, 'gid': info.pw_gid, 'home': info.pw_dir}
    except BaseException:
        raise exceptions.UserCredentialsException(
            "Parsing user information"
        )
    return user


def get_admin_token(path):
    try:
        token_store = utils.read_yaml_file(path)
        token = token_store['prolog']['token']
    except IOError:
        raise exceptions.UserCredentialsException(
            "No admin credentials"
        )
    except BaseException:
        raise exceptions.ParseException(
            "Token not found"
        )
    return token


def write_user_credentials(token, file_path):
    out = open(file_path,'w')
    out.write(token) # todo: control several jobs
    out.close()


def print_message(message, type='OK'):
    if not isinstance(message, list):
        message = [message]
    print
    for m in message:
        m = colors[type] + m + colors['ENDC']
        print '{:<}'.format(m)
    print


def print_error(e):
    print_message(e.message, 'FAIL')


def print_table(headers, rows, title=None, err=False):
    try:
        if headers:
            print
            if title:
                if err:
                    message = colors['FAIL'] + ' ERROR ' + colors['ENDC']
                else:
                    message = colors['OK'] + title.upper() + colors['ENDC']

                print '   =====> {:<} <====='.format(message)
            print tabulate(
                rows, headers=headers,
                tablefmt="plain", numalign="left"
            )
            print
    except Exception as e:
        print e.message


def parse_volume(ctx, param, value):
    result = None
    if value:
        try:
            # /root/docker_test/:/tmp
            volume_info = value.split(":")
            h_dir = volume_info[0]
            docker_dir = volume_info[1]
            result = {"host_dir": h_dir,"docker_dir": docker_dir}
        except Exception:
            raise exceptions.ParseException(
                "%s is not an absolute path" % value
            )
    return result
