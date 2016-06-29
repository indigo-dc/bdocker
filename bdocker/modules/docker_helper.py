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
import docker as docker_py

from bdocker import exceptions
from bdocker import parsers

# sys.tracebacklimit = 0

class DockerController(object):

    def __init__(self, url, cgroup=None):
        # tls_config = docker.tls.TLSConfig(
        #     client_cert=('/path/to/client-cert.pem', '/path/to/client-key.pem')
        # )
        self.control = docker_py.Client(base_url=url, version='1.19')

    def pull_image(self, repo, tag='latest'):
        try:
            docker_out = self.control.pull(repository=repo,
                                           tag=tag, stream=True)
            result = parsers.parse_docker_generator(docker_out)
        except BaseException as e:
            raise exceptions.DockerException(e)
        return result

    def delete_image(self, image_id):
        try:
            docker_out = self.control.remove_image(container=image_id)
            return docker_out
        except BaseException as e:
            raise exceptions.DockerException(e)

    def delete_container(self, container_id, force=False):
        try:
            self.control.remove_container(
                container_id, force=force
            )
            return  container_id
        except BaseException as e:
            raise exceptions.DockerException(e)

    def clean_containers(self, containers, force=True):
        docker_out = []
        if containers:
            for c_id in containers:
                try:
                    self.delete_container(c_id, force=force)
                    docker_out.append(c_id)
                except exceptions.DockerException as e:
                    docker_out.append(e.message)
        return docker_out

    def list_containers_details(self, containers):
        result = []
        try:
            for container_id in containers:
                docker_out = self.control.inspect_container(container_id)
                container_row = parsers.parse_list_container_details(docker_out)
                result.append(container_row)
        except BaseException as e:
            raise exceptions.DockerException(e)
        return result

    def list_containers(self, containers, all=False):
        result = []
        try:
            docker_containers = self.control.containers(all=all)
            for c in containers:
               for d_c in docker_containers:
                    if c in d_c["Id"]:
                        d_c['Id'] = c[:12]
                        # it set the short id like in docker
                        container_row = parsers.parse_list_container(d_c)
                        result.append(container_row)
        except BaseException as e:
            raise exceptions.DockerException(e)
        return result

    def container_details(self, container_id):
        try:
            docker_out = self.control.inspect_container(container_id)
            details = parsers.parse_inspect_container(docker_out)
        except BaseException as e:
            raise exceptions.DockerException(e)
        return details

    def logs_container(self, container_id):
        try:
            docker_out = self.control.logs(container=container_id,
                                           stdout=True,
                                           stderr=True,
                                           stream=True)
            out = parsers.parse_docker_log(docker_out)
        except BaseException as e:
            raise exceptions.DockerException(e)
        return out

    def start_container(self, container_id, detach=False):
        try:
            self.control.start(container=container_id)
        except BaseException as e:
            raise exceptions.DockerException(e)

    def run_container(self, image_id, detach, command,
                      working_dir=None, host_dir=None, docker_dir=None,
                      cgroup=None):
        try:
            binds = None
            if host_dir:
                binds = ['%s:%s' % (host_dir, docker_dir)]
            host_config = self.control.create_host_config(
                binds=binds,
                cgroup_parent=cgroup
                )
            container_info = self.control.create_container(
                image=image_id,
                command=command,
                detach=detach,
                host_config=host_config,
                working_dir=working_dir
                # volumes=volumes
            )
            if 'Id' not in container_info:
                # TODO(jorgesece): check warnings
                raise exceptions.DockerException()
            container_id = container_info['Id']
        except BaseException as e:
            raise exceptions.DockerException(e)
        return container_id

    def copy_from_container(self, container_id, container_path,
                            host_path):
        try:
            docker_out, stat = self.control.get_archive(
                container=container_id, path=container_path)
        except BaseException as e:
            raise exceptions.DockerException(e)
        return docker_out

    def copy_to_container(self, container_id, container_path,
                          host_path):
        try:
            stat = self.control.put_archive(
                container=container_id, path=container_path,
                data=host_path)
        except BaseException as e:
            raise exceptions.DockerException(e)
        return stat


# NO IMPLEMENTED

    def stop_container(self, container_id):
        self.control.stop(container=container_id)
        return "stop container"

    def accounting_container(self, container_id):
        raise exceptions.DockerException()


