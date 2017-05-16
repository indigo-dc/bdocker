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
from bdocker import utils


class DockerController(object):

    def __init__(self, url, cgroup=None):
        try:
            self.control = docker_py.Client(base_url=url, version='1.20')
        except BaseException as e:
            message = ("Unable to connect to the docker server: %s" %
                       e.message)
            raise exceptions.DockerException(message=message)

    def pull_image(self, repo, tag='latest'):
        """Pull the image from a reporitory

        :param repo: image repository
        :param tag: tag for the image
        :return: dict with the messages parsed like docker makes
        """
        try:
            docker_out = self.control.pull(repository=repo,
                                           tag=tag, stream=True)
            result = parsers.parse_docker_generator(docker_out)
        except BaseException as e:
            raise exceptions.DockerException(e)
        return result

    def delete_image(self, image_id):
        """Remove an image from the docker cache.

        :param image_id: image id
        :return: return the docker api output
        """
        try:
            docker_out = self.control.remove_image(container=image_id)
            return docker_out
        except BaseException as e:
            raise exceptions.DockerException(e)

    def delete_container(self, container_id, force=False):
        """Remove a container from the docker cache.

        :param container_id: container id
        :param force: boolean, force to stop containers
        :return: container id
        """
        try:
            self.control.remove_container(
                container_id, force=force
            )
            return container_id
        except BaseException as e:
            raise exceptions.DockerException(e)

    def clean_containers(self, containers, force=True):
        """Delete all containers from the docker cache.

        :param containers: list of containers
        :param force: boolean, force to stop containers
        :return: message from delete each container
        """
        docker_out = []
        if containers:
            for c_id in containers:
                try:
                    self.delete_container(c_id, force=force)
                    docker_out.append(c_id)
                except exceptions.DockerException as e:
                    docker_out.append(e.message)
                except BaseException as e:
                    raise exceptions.DockerException(e)
        return docker_out

    def list_containers_details(self, containers):
        """List the details of each container of a user.

        Give the details of each container.

        :param containers: list of containers
        :return: list of container details
        """
        result = []
        try:
            for container_id in containers:
                docker_out = self.control.inspect_container(container_id)
                container_row = parsers.parse_list_container_details(
                    docker_out)
                result.append(container_row)
        except BaseException as e:
            raise exceptions.DockerException(e)
        return result

    def list_containers(self, containers, all=False):
        """List containers of a user.

        List brief description of each container, such as
        docker client makes on ps.

        :param containers: list of containers
        :param all: indicates all conainers (finished too)
        :return:
        """
        result = []
        try:
            docker_containers = self.control.containers(
                all=all
            )
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
        """Return the details of a specific container

        :param container_id:
        :return: container details
        """
        try:
            docker_out = self.control.inspect_container(container_id)
            details = parsers.parse_inspect_container(docker_out)
        except BaseException as e:
            raise exceptions.DockerException(e)
        return details

    def logs_container(self, container_id):
        """Return the log of a contanier.

        :param container_id:
        :return: log information
        """
        try:
            docker_out = self.control.logs(container=container_id,
                                           stdout=True,
                                           stderr=True,
                                           stream=True,
                                           timestamps=False,
                                           tail='all',
                                           since=None,
                                           follow=None)
            out = parsers.parse_docker_log(docker_out)
        except BaseException as e:
            raise exceptions.DockerException(e)
        return out

    def start_container(self, container_id, detach=False):
        """Start the container.

        :param container_id: container id
        :param detach: [DEPRECATED]
        :return:
        """
        try:
            self.control.start(container=container_id)
        except BaseException as e:
            raise exceptions.DockerException(e)

    def run_container(self, image_id, detach, command,
                      working_dir=None, host_dir=None, docker_dir=None,
                      cgroup=None):
        """Run script in the container.

        Run the script in the container already started.

        :param image_id: image id
        :param detach: detach the container execution
        :param command: script or command to execute
        :param working_dir: work dir in the working node
        :param host_dir: container directory to bind
        :param docker_dir: host directory to bind
        :param cgroup: cgroup in which run the container
        :return: container id
        """
        try:
            binds = None
            # FIXME(A1ve5): trying this; I'll sort it out later
            # FIXME(A1ve5): Error:
            #               "Got unexpected extra arguments (create_network
            #               is not available for version < 1.21)"
            # self.control.create_network("network1", driver="bridge")
            if host_dir:
                binds = ['%s:%s' % (host_dir, docker_dir)]
            host_config = self.control.create_host_config(
                binds=binds,
                cgroup_parent=cgroup,
                network_mode='bridge'
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
                            host_path, uid=None, gid=None):
        """Copy data from container to host

        Copy files from a path in container to a path in the
        HOME user directory. Set as owner of the file the
        user uid and gid.

        :param container_id: container id
        :param container_path: container path
        :param host_path: host pat
        :param uid: user uid
        :param gid: user gid
        :return: stat retrieved from the docker api
        """
        try:
            docker_out, stat = self.control.get_archive(
                container=container_id, path=container_path)
            utils.write_tar_raw_data_stream(host_path,
                                            docker_out.data,
                                            uid, gid)
        except BaseException as e:
            raise exceptions.DockerException(e)
        return stat

    def copy_to_container(self, container_id, container_path,
                          host_path):
        """Copy files from the host to a container.

        :param container_id: container id
        :param container_path: container path
        :param host_path: host path
        :return: stat retrieved by the docker api
        """
        try:
            data = utils.read_tar_raw_data_stream(host_path)
            stat = self.control.put_archive(
                container=container_id, path=container_path,
                data=data)
        except BaseException as e:
            raise exceptions.DockerException(e)
        return stat

    def stop_container(self, container_id):
        try:
            # timeout - Seconds to wait for stop before killing it. Default: 10
            stat = self.control.stop(container=container_id, timeout=10)
        except BaseException as e:
            raise exceptions.DockerException(e)
        return stat

    def info(self):
        try:
            docker_out = self.control.info()
            info = parsers.parse_docker_info(docker_out)
        except BaseException as e:
            raise exceptions.DockerException(e)
        return info

# NOT IMPLEMENTED
