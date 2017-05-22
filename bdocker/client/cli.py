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
import tabulate

from bdocker.client import commands
from bdocker.client import decorators
from bdocker import exceptions


def print_message(message):
    """Print message

    :param message: message list
    """
    if isinstance(message, dict):
        m = []
        for k, v in message.items():
            m.append("%s: %s" % (k, v))
        message = m
    if not isinstance(message, list):
        message = [message]
    for m in message:
        print(m)


def print_error(message):
    """Print message  error

    :param message: message list
    """
    print_message(message)


def print_table(headers, rows):
    """Print table from list of messages.

    :param headers: table headers
    :param rows: row of messages
    """
    try:
        if headers:
            print('\n')
            print(tabulate.tabulate(
                rows, headers=headers,
                tablefmt="plain", numalign="left"
            ))
            print('\n')
    except Exception as e:
        print(e.message)


@click.group()
@click.version_option()
@decorators.endpoint_argument
@click.pass_context
def bdocker(ctx, host):
    """Manages docker execution on batch systems.

    :param ctx: context
    :param host: endpoint optional to the one in
     configuration file
    :return: None
    """
    ctx.obj = commands.CommandController(endpoint=host)


@bdocker.command('configure',
                 help="Configution of the environment."
                      "It request for user token and"
                      "prepare the batch environment."
                      " ROOT privileges needed")
@decorators.user_option
@click.pass_context
def configure_environment(ctx, user):
    """Configure credentials and batch environment.

    It creates a token credential for the user, and
    configure the batch environment to run dockers
    and control de accounting.
    Command executed by the root in prolog

    :param ctx: context
    :param user: user uid, optional
    :param jobid: jobid, optional
    :return:
    """
    try:
        out = ctx.obj.configuration(
            user
        )
        print_message(out["path"])
    except BaseException as e:
        print_error(e.message)


@bdocker.command('clean',
                 help="Clean work environment including"
                      "the batch system. Force remove all the"
                      " ROOT privileges needed")
@decorators.token_option
@click.pass_context
def clean_environment(ctx, token):
    """Clean credentials and batch environment.

    It cleans a token credential for the user, and
    the batch environment, in addition to delete all
    dockers. Also,
    Command executed by the root in prolog

    :param ctx: context
    :param token: token, optional
    :return:
    """

    try:
        out = ctx.obj.clean_environment(token)
        print_message(out)
    except BaseException as e:
        print_error(e.message)


@bdocker.command('pull',
                 help="Pull a image.")
@decorators.token_option
@decorators.source_argument
@click.pass_context
def container_pull(ctx, token, source):
    """Pull image from repository

    :param ctx: context
    :param token: token, optional
    :param source: repository
    :return:
    """
    try:
        out = ctx.obj.container_pull(token, source)
        print_message(out)
    except BaseException as e:
        print_error(e.message)


@bdocker.command('run', help="Creates a writeable container "
                             "layer over the specified image,"
                             " and executes the command.")
@decorators.token_option
@decorators.image_id_argument
@decorators.command_argument
@decorators.d_option
@decorators.workdir_option
@decorators.volume_option
@click.pass_context
def container_run(ctx, token, image_id,
                  script, detach, workdir, volume):
    """Run container

    :param ctx: context
    :param token: token, optional
    :param image_id: image id
    :param script: script to execute
    :param detach: detach the container, unsynchorinized
    :param workdir: work dir
    :param volume: volume to bind
    :return:
    """
    # NOTE(jorgesece): parameter detach doesn't allow assing
    # a value. It is just a flag (true/false)
    try:
        out = ctx.obj.container_run(
            token, image_id, detach, script,
            workdir,
            volume
        )
        print_message(out)
    except BaseException as e:
        print_error(e.message)


@bdocker.command('ps', help="Show all containers running.")
@decorators.token_option
@decorators.all_option
@click.pass_context
def container_list(ctx, token, all):
    """List all the containers running

    :param ctx: context
    :param token:token, optional
    :param all: boolean, all containers
    :return:
    """
    try:
        out = ctx.obj.container_list(token, all)
        headers = ['CONTAINER ID', 'IMAGE', 'COMMAND',
                   'CREATED', 'STATUS', 'PORTS', 'NAMES']
        print_table(headers, out)
    except BaseException as e:
        print_error(e.message)


@bdocker.command('logs', help="Retrieves logs present at"
                              " the time of execution.")
@decorators.token_option
@decorators.container_id_argument
@click.pass_context
def container_logs(ctx, token, container_id):
    """Show the log of a container

    :param ctx: context
    :param token: token, optional
    :param container_id: container id
    :return:
    """
    try:
        out = ctx.obj.container_logs(token, container_id)
        print_message(out)
    except BaseException:
        m = ("Error: No container related to %s" %
             container_id)
        print_error(m)


@bdocker.command('inspect', help="Return low-level"
                                 " information "
                                 "on a container or image")
@decorators.token_option
@decorators.container_id_argument
@click.pass_context
def container_inspect(ctx, token, container_id):
    """Return the low level information

    :param ctx: context
    :param token: token, optional
    :param container_id: container id
    :return:
    """
    try:
        out = ctx.obj.container_inspect(token, container_id)
        print_message(out)
    except BaseException:
        m = ("Error: No such container: %s" %
             container_id)
        print_error(m)


@bdocker.command('rm', help="Delete a container.")
@decorators.token_option
@decorators.container_ids_argument
@decorators.force_option
@click.pass_context
def container_delete(ctx, token, container_ids, force):
    """Delete a container or list of them.

    :param ctx: context
    :param token: token, optional
    :param container_ids: container ids
    :param force: force delete containers
    :return:
    """
    try:
        out = ctx.obj.container_delete(token, container_ids, force)
        print_message(out)
    except exceptions.DockerException as e:
        m = e.message
        print_error(m)


@bdocker.command('cp',
                 help="Copy files/folders between "
                      "a container and the local filesystem:\n"
                      "1) <containerId>:/file/path/within/container"
                      " /host/path/target\n"
                      "2) /host/path/target <containerId>:"
                      "/file/path/within/container")
@decorators.token_option
@decorators.path_argument
@click.pass_context
def copy(ctx, token, path):
    """Copy files/folders

    Copy files/folders between a container and
    the local filesystem.

    :param ctx: context
    :param token: token, optional
    :param path: path with the appropiate format
    :return:
    """
    try:
        container_id = path["container_id"]
        container_path = path["container_path"]
        host_path = path["host_path"]
        host_to_container = path["host_to_container"]
        out = ctx.obj.copy_to_from_container(token,
                                             container_id,
                                             container_path,
                                             host_path,
                                             host_to_container)
        print_message(out)
    except BaseException as e:
        print_error(e.message)


@bdocker.command('stop',
                 help="Stop container")
@decorators.token_option
@decorators.container_id_argument
@click.pass_context
def stop(ctx, token, container_id):
    try:
        out = ctx.obj.container_stop(token, container_id)
        print_message(out)
    except BaseException as e:
        print_error(e.message)


@bdocker.command('info',
                 help="Docker info")
@decorators.token_option
@click.pass_context
def info(ctx, token):
    try:
        out = ctx.obj.docker_info(token)
        print_message(out)
    except BaseException as e:
        print_error(e.message)


@bdocker.command('start',
                 help="Starts container")
@decorators.token_option
@decorators.container_id_argument
@click.pass_context
def start(ctx, token, container_id):
    try:
        out = ctx.obj.container_start(token, container_id)
        print_message(out)
    except BaseException as e:
        print_error(e.message)