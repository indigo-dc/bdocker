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
import ConfigParser
import json
import os
import pwd
from tabulate import tabulate
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


def load_configuration():
    token_store = os.getenv(
        'BDOCKER_TOKEN_STORE',
        '/root/.bdocker_token_store.yaml')
    endpoint = os.getenv(
        'BDOCKER_ENDPOINT',
        'http://localhost:5000')
    token_file = os.getenv(
        'BDOCKER_USER_TOKEN_FILE',
        '.bdocker_token')
    return {'token_store':token_store,
            'endpoint': endpoint,
            'token_file': token_file
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
        home_dir = os.path.realpath(info.pw_dir)
        user = {'uid': uid, 'gid': info.pw_gid, 'home': home_dir}
    except BaseException:
        raise exceptions.UserCredentialsException(
            "User not found"
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
    if isinstance(message, dict):
        m = []
        for k,v in message.items():
            m.append("%s: %s" % (k,v))
        message = m
    if not isinstance(message, list):
        message = [message]
    for m in message:
        print m

def print_error(message):
    print_message(message)


def print_message_color(message, type='OK'):
    if isinstance(message, dict):
        m = []
        for k,v in message.items():
            m.append("%s: %s" % (k,v))
        message = m
    if not isinstance(message, list):
        message = [message]
    # print
    for m in message:
        # m = colors[type] + m + colors['ENDC']
        # print '{:<}'.format(m)
        print m
    # print


def print_error_color(message):
    print_message(message, 'FAIL')


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


def parse_bool(ctx, param, value):
    if value:
        if value == 'True' or value == 'true':
            return True
        elif value == 'False' or value == 'false':
            return False
        else:
            raise exceptions.ParseException(
                'Value error: %s' % value
            )