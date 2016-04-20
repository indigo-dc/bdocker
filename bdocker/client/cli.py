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
from bdocker.client.controller import  utils

sys.tracebacklimit=0


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
        utils.print_error(e)


@bdocker.command('pull',
                 help="Pull a container and"
                      " its intermediate layers.")
@token_argument
@source_argument
@click.pass_context
def container_pull(ctx, token, source):
    try:
        out = ctx.obj.container_pull(token, source)
        utils.print_message("Container id: %s" % out)
    except BaseException as e:
        utils.print_error(e)


@bdocker.command('rm', help="Delete a container.")
@token_argument
@container_id_argument
@click.pass_context
def container_delete(ctx, token, container_id):
    try:
        out = ctx.obj.container_delete(token, container_id)
        utils.print_message("Deleted container: %s" % out)
    except BaseException as e:
            utils.print_error(e)


@bdocker.command('ps', help="Show all containers running.")
@token_argument
@click.pass_context
def container_list(ctx, token):
    try:
        out = ctx.obj.container_list(token)
        utils.print_message("List in table: %s" % out)
    # todo: list in table
    except BaseException as e:
            utils.print_error(e)


@bdocker.command('logs', help="Retrieves logs present at"
                              " the time of execution.")
@token_argument
@container_id_argument
@click.pass_context
def container_logs(ctx, token, container_id):
    try:
        out = ctx.obj.container_logs(token, container_id)
        utils.print_message("List in table: %s" % out)
    # todo: list in table
    except BaseException as e:
            utils.print_error(e)


@bdocker.command('start',
                 help="Stop a container"
                      " by sending SIGTERM.")
@token_argument
@container_id_argument
@click.pass_context
def container_start(ctx, token, container_id):
    try:
        out = ctx.obj.container_start(token, container_id)
        utils.print_message("Started container: %s" % out)
    except BaseException as e:
            utils.print_error(e)


@bdocker.command('stop', help="Start a container.")
@token_argument
@container_id_argument
@click.pass_context
def container_stop(ctx, token, container_id):
    try:
        out = ctx.obj.container_stop(token, container_id)
        utils.print_message("Stoped container: %s" % out)
    except BaseException as e:
            utils.print_error(e)


@bdocker.command('run', help="Creates a writeable container "
                             "layer over the specified image,"
                             " and executes the command.")
@token_argument
@container_id_argument
@command_argument
@click.pass_context
def container_run(ctx, token, container_id, script):
    try:
        out = ctx.obj.task_run(token, container_id, script)
        utils.print_message("Script executed in job: %s" % out)
    except BaseException as e:
            utils.print_error(e)


@bdocker.command('accounting',
                 help="Retrieve the job accounting.")
@token_argument
@container_id_argument
@click.pass_context
def accounting(ctx, token, container_id):
    try:
        out = ctx.obj.accounting_retrieve(token, container_id)
        utils.print_message("List in table: %s" % out)
    # todo: list in table
    except BaseException as e:
            utils.print_error(e)
