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

from bdocker import exceptions
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
        parameters = dict
        try:
            parameters["user_credentials"] = utils.get_user_credentials()
            results = self.control.execute_put(path=path, parameters=parameters)
            # todo(jorgesece): implement print results
            click.echo("create_token")
        except exceptions.UserCredentialsException as e:
            click.echo(e.message)
        except Exception as e:
            raise click.ClickException(e.message)

    def container_pull(self, token, source):
        path = "/pull"
        parameters = dict
        parameters["user_token"] = token
        parameters["container_source"] = source
        try:
            results = self.control.execute_post(path=path, parameters=parameters)
            # todo(jorgesece): implement print results
            click.echo("container_pull")
        except exceptions.UserCredentialsException as e:
            click.echo(e.message)
        except Exception as e:
            raise click.ClickException(e.message)

    def container_delete(self, token, container_id):
        path = "/delete"
        parameters = dict
        parameters["user_token"] = token
        parameters["container_id"] = container_id
        try:
            results = self.control.execute_delete(path=path, parameters=parameters)
            # todo(jorgesece): implement print results
            click.echo("container_delete")
        except exceptions.UserCredentialsException as e:
            click.echo(e.message)
        except Exception as e:
            raise click.ClickException(e.message)


    def container_list(self, token, container_id):
        path = "/ps"
        parameters = dict
        parameters["user_token"] = token
        parameters["container_id"] = container_id
        try:
            results = self.control.execute_get(path=path, parameters=parameters)
            # todo(jorgesece): implement print results
            click.echo("container_list")
        except exceptions.UserCredentialsException as e:
            click.echo(e.message)
        except Exception as e:
            raise click.ClickException(e.message)

    def container_logs(self, token, container_id):
        path = "/logs"
        parameters = dict
        parameters["user_token"] = token
        parameters["container_id"] = container_id
        try:
            results = self.control.execute_get(path=path, parameters=parameters)
            # todo(jorgesece): implement print results
            click.echo("container_logs")
        except exceptions.UserCredentialsException as e:
            click.echo(e.message)
        except Exception as e:
            raise click.ClickException(e.message)

    def container_start(self, token, container_id):
        path = "/start"
        parameters = dict
        parameters["user_token"] = token
        parameters["container_id"] = container_id
        try:
            results = self.control.execute_post(path=path, parameters=parameters)
            # todo(jorgesece): implement print results
            click.echo("container_start")
        except exceptions.UserCredentialsException as e:
            click.echo(e.message)
        except Exception as e:
            raise click.ClickException(e.message)

    def container_stop(self, token, container_id):
        path = "/stop"
        parameters = dict
        parameters["user_token"] = token
        parameters["container_id"] = container_id
        try:
            results = self.control.execute_post(path=path, parameters=parameters)
            # todo(jorgesece): implement print results
            click.echo("container_stop")
        except exceptions.UserCredentialsException as e:
            click.echo(e.message)
        except Exception as e:
            raise click.ClickException(e.message)

    def task_run(self, token, container_id):
        path = "/run"
        parameters = dict
        parameters["user_token"] = token
        parameters["container_id"] = container_id
        try:
            results = self.control.execute_post(path=path, parameters=parameters)
            # todo(jorgesece): implement print results
            click.echo("container_run")
        except exceptions.UserCredentialsException as e:
            click.echo(e.message)
        except Exception as e:
            raise click.ClickException(e.message)

    def accounting_retrieve(self, token, container_id):
        path = "/accounting"
        parameters = dict
        parameters["user_token"] = token
        parameters["container_id"] = container_id
        try:
            results = self.control.execute_get(path=path, parameters=parameters)
            # todo(jorgesece): implement print results
            click.echo("accounting_retrieve")
        except exceptions.UserCredentialsException as e:
            click.echo(e.message)
        except Exception as e:
            raise click.ClickException(e.message)
