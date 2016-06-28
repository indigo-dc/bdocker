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

import click

from bdocker import exceptions

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

def endpoint_argument(f):
    return click.option(
        '--host', '-H', default=False
        , type=click.STRING
        , help='BDocker server endpoint'
    )(f)


def token_argument(f):
    return click.argument('token'
                          , type=click.STRING
                          # callback=client_utils.get_id_from_name
                          # fixme(jorgesece): control token
                          )(f)


def token_option(f):
    return click.option(
        '--token', '-t', default=None
        , type=click.STRING
        , help='The token ID'
    )(f)


def job_option(f):
    return click.option(
        '--jobid', '-j', default=None
        , type=click.INT
        , help='The job ID'
    )(f)


def source_argument(f):
    return click.argument('source'
                          , type=click.STRING
                          )(f)


def container_id_argument(f):
    return click.argument("container_id"
                          , type=click.STRING
                          )(f)


def container_ids_argument(f):
    return click.argument("container_ids"
                          , type=click.STRING
                          , nargs=-1
                          , required=True
                          )(f)


def image_id_argument(f):
    return click.argument("image_id"
                          , type=click.STRING
                          )(f)

def command_argument(f):
    return click.argument("script"
                          , type=click.STRING
                          )(f)


def user_credentials(f):
    out = click.argument("uid"
                         , type=click.INT
                         )(f)
    return out


def user_option(f):
    return click.option(
        '--user', '-u', default=None
        , type=click.STRING
        , help='User name'
    )(f)


def d_option(f):
    return click.option(
        '--detach', '-d', default=False
        , type=click.BOOL, is_flag=True
        , help='Run container in background and print container ID'
    )(f)


def all_option(f):
    return click.option(
        '--all', '-a', default=False
        , type=click.BOOL, is_flag=True
        , help='Show all containers (default shows just running)'
    )(f)


def force_option(f):
    return click.option(
        '--force', '-f', default=False
        , type=click.BOOL, is_flag=True
        , help='Force the removal of a running container (uses SIGKILL)'
    )(f)


def force_option_clean(f):
    return click.option(
        '--force', '-f', default=True
        , type=click.BOOL, is_flag=True
        , help='Force the removal of a running container (uses SIGKILL)'
    )(f)

def volume_option(f):
    return click.option(
        '--volume', '-v', default=None, type=click.STRING
        , callback=parse_volume
        , help='Bind mount a volume'
    )(f)


def workdir_option(f):
    return click.option(
        '--workdir', '-w', default=None, type=click.STRING
        , help='Working directory inside the container'
    )(f)
