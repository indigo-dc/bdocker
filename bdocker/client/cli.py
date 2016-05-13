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
import sys

from bdocker.client.controller import commands
from bdocker.client.decorators import *
from bdocker.client.controller import utils


@click.group()
@click.version_option()
@click.pass_context
def bdocker(ctx):
    """Manages docker execution on batch systems."""
    ctx.obj = commands.CommandController()


@bdocker.command('credentials',
                 help="Request for user token.")
@user_credentials
@click.pass_context
def credentials_create(ctx, uid):
    # Command executed by the root in prolog
    try:
        out = ctx.obj.create_credentials(uid)
        utils.print_message(
            "User token: %s Path: %s"
            % (out["token"], out["path"])
        )
    except BaseException as e:
        utils.print_error(e.message)


@bdocker.command('pull',
                 help="Pull a container and"
                      " its intermediate layers.")
@token_argument
@source_argument
@click.pass_context
def container_pull(ctx, token, source):
    try:
        out = ctx.obj.container_pull(token, source)
        utils.print_message(out)
    except BaseException as e:
        utils.print_error(e.message)


@bdocker.command('run', help="Creates a writeable container "
                             "layer over the specified image,"
                             " and executes the command.")
@token_argument
@image_id_argument
@command_argument
@d_option
@workdir_option
@volume_option
@click.pass_context
def container_run(ctx, token, image_id,
                  script, detach, workdir, volume):
    try:
        out = ctx.obj.container_run(
            token, image_id, detach, script,
            workdir,
            volume
        )
        utils.print_message(out)
    except BaseException as e:
        utils.print_error(e.message)


@bdocker.command('ps', help="Show all containers running.")
@token_argument
@all_option
@click.pass_context
def container_list(ctx, token, all):
    try:
        out = ctx.obj.container_list(token, all)
        headers = ['CONTAINER ID', 'IMAGE', 'COMMAND',
                   'CREATED', 'STATUS', 'PORTS', 'NAMES']
        utils.print_table(headers, out)
    except BaseException as e:
        utils.print_error(e.message)


@bdocker.command('logs', help="Retrieves logs present at"
                              " the time of execution.")
@token_argument
@container_id_argument
@click.pass_context
def container_logs(ctx, token, container_id):
    try:
        out = ctx.obj.container_logs(token, container_id)
        utils.print_message(out)
    except BaseException as e:
        utils.print_error(e.message)


@bdocker.command('inspect', help="Return low-level"
                                 " information "
                                 "on a container or image")
@token_argument
@container_id_argument
@click.pass_context
def container_inspect(ctx, token, container_id):
    try:
        out = ctx.obj.container_inspect(token, container_id)
        utils.print_message(out)
    except BaseException as e:
        m = ("Error: failed to remove containers: [%s]" %
             container_id)
        utils.print_error(m)


@bdocker.command('rm', help="Delete a container.")
@token_argument
@container_id_argument
@click.pass_context
def container_delete(ctx, token, container_id):
    try:
        out = ctx.obj.container_delete(token, container_id)
        utils.print_message(out)
    except BaseException as e:
        m = ("Error: failed to remove containers: [%s]" %
             container_id)
        utils.print_error(m)


@bdocker.command('accounting',
                 help="Retrieve the job accounting.")
@token_argument
@container_id_argument
@click.pass_context
def accounting(ctx, token, container_id):
    try:
        out = ctx.obj.accounting_retrieve(token, container_id)
        utils.print_message(out)
    except BaseException as e:
        utils.print_error(e.message)