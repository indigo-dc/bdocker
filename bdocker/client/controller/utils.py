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
import six.moves.urllib.parse as urlparse

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
    """Load configuration from environment variables

    DEPRECATED

    :param key: name of variable
    :param key: value of variable
    """
    token_store = os.getenv(
        'BDOCKER_TOKEN_STORE',
        '/root/.bdocker_token_store.yaml')
    endpoint = os.getenv(
        'BDOCKER_ENDPOINT',
        'http://localhost:5000')
    token_file = os.getenv(
        'BDOCKER_TOKEN_FILE',
        '.bdocker_token')
    job_id = os.getenv(
        'JOB_ID',
        None)

    return {'token_store':token_store,
            'endpoint': endpoint,
            'token_file': token_file,
            'job_id': job_id
            }


def set_environ(key, value):
    """Set variable in environment

    :param key: name of variable
    :param key: value of variable
    """
    os.environ[key] = value


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
    """Get request query string from parameters

    :param name: name of the user
    """
    if parameters is None:
        query_string = None
    else:
        query_string = urlparse.urlencode(parameters)
    return query_string


def make_body(parameters):
    """Create json body request

    :param parameters: dict of parameters to include
    """
    body = {}
    for key in parameters.keys():
        body[key] = parameters[key]

    return json.dumps(body)


def get_user_credentials(name):
    """Read user information from user

    :param name: name of the user
    """
    try:
        info = pwd.getpwnam(name)
        home_dir = os.path.realpath(info.pw_dir)
        user = {'uid': info.pw_uid, 'gid': info.pw_gid,
                'home': home_dir}
    except BaseException:
        raise exceptions.UserCredentialsException(
            "User %s not found: " % name
        )
    return user


def get_admin_token(path):
    """Get admin token from path file

    :param path: file to be read
    """
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


def write_user_credentials(token, file_path,
                           uid=None, gid=None):
    """Write token in file and change its owner,

    :param token: token ID
    :param file_path: file to write it
    :param uid: user id
    :param gid: user group id
    """
    out = open(file_path,'w')
    out.write(token)
    # set_environ('BDOCKER_TOKEN_FILE',
    # file_path)
    out.close()
    if uid:
        os.chown(file_path, uid, gid)


def read_user_credentials(file_path):
    """Read token file in YAML format

    :param token: token of the registry
    :param fields: array of element to be updated
    """
    input = open(file_path,'r')
    token = input.read().rstrip('\n')
    input.close()
    return token


def print_message(message):
    """Print message

    :param message: message list
    """
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
    """Print message  error

    :param message: message list
    """
    print_message(message)


def print_message_color(message, type='OK'):
    """Print message color

    DEPRECATED: it provokes error in parse output string

    :param message: message list
    :param type: type of message
    """
    if isinstance(message, dict):
        m = []
        for k,v in message.items():
            m.append("%s: %s" % (k,v))
        message = m
    if not isinstance(message, list):
        message = [message]
    # print
    for m in message:
        m = colors[type] + m + colors['ENDC']
        print '{:<}'.format(m)
        print m
    # print


def print_error_color(message):
    """Print message error in color

    DEPRECATED: it provokes error in parse output string

    :param message: message list
    """
    print_message(message, 'FAIL')


def print_table(headers, rows, title=None, err=False):
    """Print table from list of messages

    :param headers: table headers
    :param rows: row of messages
    :param title: tile of the table
    :param err: error bool
    """
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


def token_parse(value, path):
    """Parse token

    If value is null, it read the token from the
    $HOME/.bdocker_token_$JOBID file

    :param param: parameters
    :param value: input value
    """
    try:
        if not value:
            value = read_user_credentials(path)
        return value
    except BaseException as e:
        raise exceptions.UserCredentialsException(
            "Token can not be found in %s " % path
        )


# Callbacks

def parse_volume(ctx, param, value):
    """Command Client Callback. Parse volume

    :param ctx: contex
    :param param: parameters
    :param value: input value
    """
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
    """Command Client Callback. Parse bool

    :param ctx: contex
    :param param: parameters
    :param value: input value
    """

    if value:
        if value == 'True' or value == 'true':
            return True
        elif value == 'False' or value == 'false':
            return False
        else:
            raise exceptions.ParseException(
                'Value error: %s' % value
            )
