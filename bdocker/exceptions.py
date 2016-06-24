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
import logging
import webob.exc

FORMAT = '%(asctime)-15s %(message)s'
logging.basicConfig(format=FORMAT)
logger = logging.getLogger('tcpserver')

LOG = logging.getLogger(__name__)


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
        #if 'results' in response.json_body:
        title = response.json_body['results']
        #title = response.json_body.popitem()[1].get("title")
    except Exception:
        code = 500
        message = "Unknown error happenened processing response %s" % response
        title = message
    return manage_http_exception(code, title)


def manage_http_exception(code, message):
    exc = default_exceptions.get(code, webob.exc.HTTPInternalServerError)
    return exc(message=("%s") %(message))


class BDockerException(Exception):
    def __init__(self, exc=None, message=None, code=None):
        details = get_exception_details(exc, message, code)
        self.message = details['message']
        self.code = details['code']
        LOG.exception(message)

    def __str__(self):
        return repr(self.message)


class NoImplementedException(BDockerException):

    def __init__(self, message, e=None, code=501):
        super(NoImplementedException, self).__init__(
            message=message, code=code
        )
        self.message = ("Not implemeted: %s "
                        % self.message)


class ParseException(BDockerException):
    def __init__(self, message, exc=None, code=400):
        super(ParseException, self).__init__(
            exc, message, code
        )


class UserCredentialsException(BDockerException):
    def __init__(self, message, exc=None, code=401):
        super(UserCredentialsException, self).__init__(
            exc, message, code
        )
        self.message = ("User Credentials Exception: %s "
                        % self.message)



class ConfigurationException(BDockerException):
    def __init__(self, message, exc=None, code=None):
        super(ConfigurationException, self).__init__(
            exc, message, code
        )
        self.message = ("Configuration Exception: %s "
                        % self.message)


class BatchException(BDockerException):
     def __init__(self, message, e=None, code=None):
        super(BatchException, self).__init__(
            e, message, code
        )
        self.message = ("Batch Exception: %s "
                        % self.message)


class DockerException(BDockerException):
    def __init__(self, exc=None, message=None, code=None):
        super(DockerException, self).__init__(
            exc, message, code
        )
        self.message = ("Error: %s "
                        % self.message)


class CgroupException(BDockerException):
    def __init__(self, e=None, message=None, code=None):

        super(CgroupException, self).__init__(
            e, message, code
        )
        self.message = ("Cgroup Exception: %s"
                       % self.message)


def get_exception_details(ex=None, custom_message=None,
                          custom_code=None):
    code = 500
    message = 'Internal Error'
    if ex:
        if isinstance(ex, OSError):
            if ex.errno == 13:
                message = "%s:%s" % (ex.strerror, ex.filename)
                return {"message": message,
                        "code": 401}
        if hasattr(ex, 'response') and ex.response:
            message = ex.response.text
            code = ex.response.status_code
        else:
            if hasattr(ex, 'explanation'):
                message = str(ex.explanation)
            elif hasattr(ex, 'message'):
                message = str(ex.message)
            if hasattr(ex, 'code'):
                code = ex.code
    if custom_message:
        message = custom_message
    if custom_code:
        code = custom_code
    details = {"message": message, "code": code}
    return details

