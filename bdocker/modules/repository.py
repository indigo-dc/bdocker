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

import abc

import six

from bdocker import exceptions
from bdocker import utils

FILE_NAME = "repository.yml"


@six.add_metaclass(abc.ABCMeta)
class RepositoryController(object):
    """Base of the Repository controller."""

    def __init__(self, conf):
        """Initialize controller

        :param conf: repository configuration
        :return:
        """
        try:
            self.location = conf.get("location")
        except Exception:
            raise

    def get_image(self, image):
        """Get an image from the repository

        It is different for each batch scheduler, so, this class
        does not implement it.

        :param image: image name
        :return: empty array
        """
        exceptions.NoImplementedException("Repository Controller"
                                          "is not implemented")


class FileController(RepositoryController):
    """File Repository controller."""

    def __init__(self, *args, **kwargs):
        """Initialize controller

        :param conf: dictionary with the bdocker configuration
        :return:
        """
        super(FileController, self).__init__(*args, **kwargs)

    def get_image(self, image):
        repository_file = "%s/%s" % (self.location, FILE_NAME)
        try:
            image_list = utils.read_yaml_file(repository_file)
        except Exception:
            exceptions.RepositoryException(
                message="File %s cannot be opened"
                        % repository_file,
                code=404)
        image_info = utils.parse_image_name(image)
        name = image_info["name"]
        tag = image_info["tag"]
        if name in image_list:
            if tag in image_list[name]:
                image_file = "%s/%s" % (
                    self.location,
                    image_list[name][tag]["file"]
                )
                return image_file


class DatabaseController(RepositoryController):
    """Database repository controller."""

    def __init__(self, *args, **kwargs):
        """Initialize controller

        :param conf: dictionary with the bdocker configuration
        :return:
        """
        super(DatabaseController, self).__init__(*args, **kwargs)

    def get_image(self, image):

        exceptions.NoImplementedException("Database Repository"
                                          " Controller is not implemented")


class DockerController(RepositoryController):
    """Local docker repository controller."""

    def __init__(self, *args, **kwargs):
        """Initialize controller

        :param conf: dictionary with the bdocker configuration
        :return:
        """
        super(DockerController, self).__init__(*args, **kwargs)

    def get_image(self, image):

        exceptions.NoImplementedException("Docker Repository"
                                          " Controller is not implemented")