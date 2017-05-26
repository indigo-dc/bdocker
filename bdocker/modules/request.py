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

import json

import six
import six.moves.urllib.parse as urlparse
import webob

from bdocker import exceptions


def utf8(value):
    """Try to turn a string into utf-8 if possible.

    Code is modified from the utf8 function in
    http://github.com/facebook/tornado/blob/master/tornado/escape.py
    :param value: string

    """
    if isinstance(value, six.text_type):
        return value.encode('utf-8')
    assert isinstance(value, str)
    return value


def get_query_string(parameters):
    """Get request query string from parameters

    :param parameters: parameters to include
    """
    if parameters is None:
        query_string = None
    else:
        query_string = urlparse.urlencode(parameters)
    return query_string


def make_body(parameters):
    """Create json body request

    :param parameters: dict of parameters to include
    """
    body = {}
    for key in parameters.keys():
        body[key] = parameters[key]

    return json.dumps(body)


class RequestController(object):
    resource = None

    def __init__(self, default_path="",
                 endopoint="http://127.0.0.33:5000"):
        self.default_path = default_path
        self.endpoint = endopoint

    @staticmethod
    def _get_from_response(response, data_field='results'):
        """Get json body from response.

        Retrieves the field of the json body with
        the results.

        :param response: response
        :param data_field: field to retrieve
        :return: results
        """
        if response.status_int in [200, 201, 202]:
            exceptions.make_log('debug', 'HTTP response: %s' %
                                response.status_int)
            return response.json_body[data_field]
        elif response.status_int in [204]:
            return "Non Content"
        else:
            raise exceptions.exception_from_response(response)

    def _get_req(self, path, method,
                 content_type="application/json",
                 body=None,
                 query_string=""):
        """Return a new Request object to interact with Bdocker Server.

        :param path: new path for the request
        :param content_type: new content type for the request, defaults to
                             "application/json" if not specified
        :param body: new body for the request
        :param query_string: query string for the request, defaults to an empty
                             query if not specified
        :returns: a Request object
        """
        server = self.endpoint
        environ = {}
        new_req = webob.Request.blank(path=path,
                                      environ=environ,
                                      base_url=server)
        new_req.query_string = query_string
        new_req.method = method
        if path is not None:
            new_req.path_info = path
        if content_type is not None:
            new_req.content_type = content_type
        if body is not None:
            new_req.body = utf8(body)
        return new_req

    def execute_get(self, path, parameters):
        """Execute GET request.

        This method execute a POST request on the endpoint.

        :param path: path of the request
        :param parameters: parameters to include in the request
        :return: json response
        """
        try:
            query_string = get_query_string(parameters)
            req = self._get_req(path, query_string=query_string,
                                method="GET")
            response = req.get_response()
        except Exception as e:
            response = webob.Response(status=500, body=str(e))
        json_response = self._get_from_response(response)
        return json_response

    def execute_post(self, path, parameters):
        """Execute POST request.

        This method execute a POST request on the endpoint.

        :param path: path of the request
        :param parameters: parameters to include in the request
        :return: json response
        """
        try:
            body = make_body(parameters)
            req = self._get_req(path, content_type="application/json",
                                body=body, method="POST")
            response = req.get_response()
        except Exception as e:
            response = webob.Response(status=500, body=str(e))
        json_response = self._get_from_response(response)
        return json_response

    def execute_delete(self, path, parameters):
        """Execute DELETE request.

        This method execute a DELETE request on the endpoint.

        :param path: path of the request
        :param parameters: parameters to include in the request
        :return: json response
        """
        try:
            query_string = get_query_string(parameters)
            req = self._get_req(path, method="DELETE",
                                query_string=query_string)
            response = req.get_response(None)
        except Exception as e:
            response = webob.Response(status=500, body=str(e))
        json_response = self._get_from_response(response)
        return json_response

    def execute_put(self, path, parameters):
        """Execute PUT request.

        This method execute a PUT request on the endpoint.

        :param path: path of the request
        :param parameters: parameters to include in the request
        :return: json response
        """
        try:
            body = make_body(parameters)
            req = self._get_req(path, content_type="application/json",
                                body=body, method="PUT")
            response = req.get_response()
        except Exception as e:
            response = webob.Response(status=500, body=str(e))
        json_response = self._get_from_response(response)
        return json_response
