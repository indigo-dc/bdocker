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
from bdocker.common import exceptions
from bdocker.common import utils as utils_common
from bdocker.client.controller import utils


class CommandController(object):

    def __init__(self):
        try:
            conf = utils_common.load_configuration()
            endpoint = "http://%s:%s" % (conf['server']['host'],
                                         conf['server']['port'])
            self.control = request.RequestController(endopoint=endpoint)
            self.token_file = conf["credentials"]['token_client_file']
            self.token_storage = conf["credentials"]['token_store']
        except Exception as e:
            raise click.ClickException(e.message)

    def create_credentials(self, uid):
        path = "/credentials"
        parameters = {}
        try:
            parameters["token"] = utils.get_admin_token(self.token_storage)
            user_info = utils.get_user_credentials(uid)
            home_dir = user_info.pop('home')
            parameters["user_credentials"] = user_info
            results = self.control.execute_put(path=path, parameters=parameters)
            token_path = "%s/%s" % (home_dir, self.token_file)
            utils.write_user_credentials(results, token_path)
        except IOError as e:
            raise click.ClickException(e.strerror)
        except Exception as e:
            raise click.ClickException(e.message)
        return token_path, results

    def container_pull(self, token, source):
        path = "/pull"
        parameters = {"user_token": token, "container_source": source}
        try:
            results = self.control.execute_put(path=path, parameters=parameters)
            # todo(jorgesece): implement print results
            click.echo("container_pull")
        except exceptions.UserCredentialsException as e:
            click.echo(e.message)
        except Exception as e:
            raise click.ClickException(e.message)

    def container_delete(self, token, container_id):
        path = "/delete"
        parameters = {"user_token": token, "container_id": container_id}
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
        parameters = {"user_token": token, "container_id": container_id}
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
        parameters = {"user_token": token, "container_id": container_id}
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
        parameters = {"user_token": token, "container_id": container_id}
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
        parameters = {"user_token": token, "container_id": container_id}
        try:
            results = self.control.execute_post(path=path, parameters=parameters)
            # todo(jorgesece): implement print results
            click.echo("container_stop")
        except exceptions.UserCredentialsException as e:
            click.echo(e.message)
        except Exception as e:
            raise click.ClickException(e.message)

    def task_run(self, token, container_id, script):
        path = "/run"
        parameters = {"user_token": token,
                      "container_id": container_id,
                      "script": script
                      }
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
        parameters = {"user_token": token, "container_id": container_id}
        try:
            results = self.control.execute_get(path=path, parameters=parameters)
            # todo(jorgesece): implement print results
            click.echo("accounting_retrieve")
        except exceptions.UserCredentialsException as e:
            click.echo(e.message)
        except Exception as e:
            raise click.ClickException(e.message)
