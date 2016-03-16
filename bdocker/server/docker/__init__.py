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

from docker import Client


class DockerController(object):

    def __init__(self):
        self.control = Client()

    def pull_container(self, repo):
        return "pull container"

    def delete_container(self, container_id):
        return "delete container"

    def list_containers(self, token):
        return "list container"

    def logs_container(self, container_id):
        self.control.logs(container=container_id)
        return "log container"

    def start_container(self, container_id):
        return "start container"

    def stop_container(self, container_id):
        return "stop container"

    def run_container(self, container_id, script):
        return "run container"

    def accounting_container(self, container_id):
        return "accounting of the user"

    def output_task(self, container_id):
        return "output of the task"

