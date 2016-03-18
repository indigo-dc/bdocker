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

import docker
import json

from bdocker.common import exceptions
from bdocker.server.docker import parsers


class DockerController(object):

    def __init__(self, url):
        # tls_config = docker.tls.TLSConfig(
        #     client_cert=('/path/to/client-cert.pem', '/path/to/client-key.pem')
        # )
        self.control = docker.Client(base_url=url, version='1.19')

    def pull_image(self, repo, tag='latest'):
        try:
            docker_out = self.control.pull(repository=repo,
                                           tag=tag, stream=True)
            result = parsers.parse_docker_generator(docker_out)
        except exceptions.ParseException as e:
            raise exceptions.DockerException(e.message, e.code)
        except BaseException as e:
            raise exceptions.DockerException(e.explanation,
                                             e.response.status_code)
        return result

    def delete_image(self, image_id):
        try:
            docker_out = self.control.remove_image(container=image_id)
            if docker_out is None:
                return True
        except BaseException as e:
            raise exceptions.DockerException(e.explanation,
                                             e.response.status_code)

    def delete_container(self, container_id):
        try:
            docker_out = self.control.remove_container(
                container=container_id)
            result = parsers.parse_docker_generator(docker_out,
                                                    key='Deleted')
        except exceptions.ParseException as e:
            raise exceptions.DockerException(e.message, e.code)
        except BaseException as e:
            raise exceptions.DockerException(e.explanation,
                                             e.response.status_code)
        return result

    def list_containers(self, containers):
        result = []
        try:
            for container_id in containers:
                docker_out = self.control.inspect_container(container_id)
                dict_info = parsers.parse_list_container(docker_out)
                result.append(dict_info)
        except exceptions.ParseException as e:
            raise exceptions.DockerException(e.message, e.code)
        except BaseException as e:
            raise exceptions.DockerException(e.explanation,
                                             e.response.status_code)
        return result

    def logs_container(self, container_id):
        try:
            docker_out = self.control.logs(container=container_id,
                                           stdout=True,
                                           stderr=True,
                                           stream=True)
            out = parsers.parse_docker_log(docker_out)
        except BaseException as e:
            raise exceptions.DockerException(e.explanation,
                                             e.response.status_code)
        return out

    # def start_container(self, container_id):
    #     try:
    #         docker_out = self.control.start(container=container_id)
    #     except BaseException as e:
    #         raise exceptions.DockerException(e.explanation,
    #                                          e.response.status_code)
    #     return docker_out

    def stop_container(self, container_id):
        self.control.stop(container=container_id)
        return "stop container"

    def run_container(self, image_id, command, working_dir=None):
        # todo:verify directory of working node to move things (HOME)
        # allow users to bind directories from the wd in the container
        try:
            container_info = self.control.create_container(
                image=image_id, command=command)
            self.control.start(container=container_info['Id'])
            # todo: control Id exists
        except BaseException as e:
            raise exceptions.DockerException(e.explanation,
                                             e.response.status_code)
        return container_info

    def accounting_container(self, container_id):
        raise exceptions.DockerException(500,"Not implemented")

    def output_task(self, container_id, path):
        try:
            docker_out, stat = self.control.get_archive(
                container=container_id, path=path)
        except BaseException as e:
            raise exceptions.DockerException(e.explanation,
                                             e.response.status_code)
        return docker_out
