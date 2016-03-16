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
import logging
import webob.exc

FORMAT = '%(asctime)-15s %(message)s'
logging.basicConfig(format=FORMAT)
logger = logging.getLogger('tcpserver')

default_exceptions = {
    400: webob.exc.HTTPBadRequest,
    401: webob.exc.HTTPUnauthorized,
    403: webob.exc.HTTPForbidden,
    404: webob.exc.HTTPNotFound,
    405: webob.exc.HTTPMethodNotAllowed,
    406: webob.exc.HTTPNotAcceptable,
    409: webob.exc.HTTPConflict,
    413: webob.exc.HTTPRequestEntityTooLarge,
    415: webob.exc.HTTPUnsupportedMediaType,
    429: webob.exc.HTTPTooManyRequests,
    500: webob.exc.HTTPInternalServerError,
    501: webob.exc.HTTPNotImplemented,
    503: webob.exc.HTTPServiceUnavailable,
}


def exception_from_response(response):
    """
    # Copyright 2014 CSIC
    Convert an OpenStack V2 Fault into a webob exception.

    Since we are calling the OpenStack API we should process the Faults
    produced by them. Extract the Fault information according to [1] and
    convert it back to a webob exception.

    [1] http://docs.openstack.org/developer/nova/v2/faults.html

    :param response: a webob.Response containing an exception
    :returns: a webob.exc.exception object
    """
    try:
        code = response.status_int
        title = response.json_body.popitem()[1].get("title")
    except Exception:
        code = 500
        message = "Unknown error happenened processing response %s" % response
        title = message
    ex = manage_http_exception(code, title)
    return ex


def manage_http_exception(code, message):
    exc = default_exceptions.get(code, webob.exc.HTTPInternalServerError)
    return exc(message=("%s. %s") %(exc.title, message))


class ParseException(Exception):
    def __init__(self, message):
        self.message = message
        self.code = 400

    def __str__(self):
        return repr(self.message)


class UserCredentialsException(Exception):

    def __init__(self, message):
        self.message = ("User Credentials Exception: "
                       + message)
        self.code = 401

    def __str__(self):
        return repr(self.message)


class ConfigurationException(Exception):
    def __init__(self, message):
        self.message = ("Configuration Exception: "
                       + message)

    def __str__(self):
        return repr(self.message)
