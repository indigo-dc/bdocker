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


@six.add_metaclass(abc.ABCMeta)
class RepositoryController(object):
    """Base of the Repository controller."""

    def __init__(self, conf):
        """Initialize controller

        :param conf: dictionary with the bdocker configuration
        :return:
        """

    def pull(self, image):
        """Pull an image from the repository

        It is different for each batch scheduler, so, this class
        does not implement it.

        :param image: image name
        :return: empty array
        """
        pass


class FileController(RepositoryController):
    """File Repository controller."""

    def __init__(self, *args, **kwargs):
        """Initialize controller

        :param conf: dictionary with the bdocker configuration
        :return:
        """
        super(FileController, self).__init__(*args, **kwargs)

    def pull(self, image):

        exceptions.RepositoryException(message="Not Found", code=404)


