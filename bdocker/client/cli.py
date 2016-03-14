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


from bdocker.client.controller import commands
from bdocker.client.decorators import *

#sys.tracebacklimit=0


@click.group()
@click.version_option()
@click.pass_context
def bdocker(ctx):
    """Manages docker execution on batch systems."""
    ctx.obj = commands.CommandController()


@bdocker.command('token', help="Request for user token.")
@click.pass_context
def token_create(ctx):
    ctx.obj.create_token()


@bdocker.command('pull', help="Pull a container and its intermediate layers.")
@token_argument
@source_argument
@click.pass_context
def container_pull(ctx, token, source):
    ctx.obj.container_pull(token, source)


@bdocker.command('delete', help="Delete a container.")
@token_argument
@container_id_argument
@click.pass_context
def container_delete(ctx, token, container_id):
    ctx.obj.container_delete(token, container_id)


@bdocker.command('ps', help="Show all containers running.")
@token_argument
@click.pass_context
def container_list(ctx, token):
    ctx.obj.container_list(token)


@bdocker.command('logs', help="Retrieves logs present at"
                              " the time of execution.")
@token_argument
@container_id_argument
@click.pass_context
def container_logs(ctx, token, container_id):
    ctx.obj.container_logs(token, container_id)


@bdocker.command('start', help="Stop a container by sending SIGTERM.")
@token_argument
@container_id_argument
@click.pass_context
def container_start(ctx, token, container_id):
    ctx.obj.container_start(token, container_id)


@bdocker.command('stop', help="Start a container.")
@token_argument
@container_id_argument
@click.pass_context
def container_stop(ctx, token, container_id):
    ctx.obj.container_stop(token, container_id)


@bdocker.command('run', help="Creates a writeable container "
                             "layer over the specified image,"
                             " and executes the command.")
@token_argument
@container_id_argument
@command_argument
@click.pass_context
def container_run(ctx, token, container_id, script):
    ctx.obj.task_run(token, container_id, script)


@bdocker.command('accounting', help="Retrieve the job accounting.")
@token_argument
@container_id_argument
@click.pass_context
def accounting(ctx, token, container_id):
    ctx.obj.accounting_retrieve(token, container_id)
