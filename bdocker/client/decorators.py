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

import click

from bdocker.client.controller import utils


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


def volume_option(f):
    return click.option(
        '--volume', '-v', default=None, type=click.STRING
        , callback=utils.parse_volume
        , help='Bind mount a volume'
    )(f)


def workdir_option(f):
    return click.option(
        '--workdir', '-w', default=None, type=click.STRING
        , help='Working directory inside the container'
    )(f)
