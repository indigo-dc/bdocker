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


def create_dict(code, message):
    return {'code': code, 'message': message}


class DockerController(object):

    def __init__(self):
        pass

    def pull_container(self):
        return create_dict(201, "pull container")

    def delete_container(self):
        return create_dict(204, "delete container")

    def list_container(self):
        return create_dict(200, "list container")

    def logs_container(self):
        return create_dict(200, "log container")

    def start_container(self):
        return create_dict(200, "start container")

    def stop_container(self):
        return create_dict(200, "stop container")

    def run_container(self):
        return create_dict(200, "run container")

    def accounting_user(self):
        return create_dict(200, "accounting of the user")

    def output_task(self):
        return create_dict(200, "output of the task")

