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

from bdocker.client.controller import request
from bdocker.client.controller import utils


class CommandController(object):

    def __init__(self, path_prefix):
        try:
            self.control = request.RequestController()
        except Exception as e:
            raise click.ClickException(e.message)

    def create_token(self):
        path = "/token"
        user_credentials = utils.get_user_credentials()
        parameters = dict
        parameters["user_credentials"] = user_credentials

        click.echo("create_token")

    def container_pull(self, token, source):
        path = "/pull"
        parameters = dict
        parameters["user_token"] = token
        parameters["container_source"] = source

        click.echo("container_pull")

    def container_delete(self, token, container_id):
        path = "/delete"
        parameters = dict
        parameters["user_token"] = token
        parameters["contanier_id"] = container_id

        click.echo("container_delete")

    def container_list(self, token, container_id):
        path = "/list"
        parameters = dict
        parameters["user_token"] = token
        parameters["contanier_id"] = container_id

        click.echo("container_list")

    def container_logs(self, token, container_id):
        path = "/logs"
        parameters = dict
        parameters["user_token"] = token
        parameters["contanier_id"] = container_id

        click.echo("container_logs")

    def container_start(self, token, container_id):
        path = "/start"
        parameters = dict
        parameters["user_token"] = token
        parameters["contanier_id"] = container_id

        click.echo("container_start")

    def container_stop(self, token, container_id):
        path = "/stop"
        parameters = dict
        parameters["user_token"] = token
        parameters["contanier_id"] = container_id

        click.echo("container_stop")

    def task_run(self, token, container_id):
        path = "/run"
        parameters = dict
        parameters["user_token"] = token
        parameters["contanier_id"] = container_id

        click.echo("container_run")

    def accounting_retrieve(self, token, container_id):
        path = "/accounting"
        parameters = dict
        parameters["user_token"] = token
        parameters["contanier_id"] = container_id

        click.echo("accounting_retrieve")
