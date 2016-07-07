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

import flask
import webob

from bdocker import exceptions


def eval_bool(s):
    if s:
        if s == 'True' or str(s) == "True":
            return True
        else:
            return False


def validate(fields, mandatory_keys):
    try:
        for key in mandatory_keys:
            if key not in fields:
                raise webob.exc.HTTPBadRequest(
                    "The '%s' field is mandatory."
                    "" % key)
    except Exception:
        raise exceptions.ParseException("Validation of required values")
    return True


def make_json_response(status_code, description):
    return flask.jsonify({
        'status_code': status_code,
        'results': description
    }), status_code


def error_json_handler(exception):
    ex = exceptions.manage_http_exception(exception.code, exception.message)
    response = make_json_response(ex.code, ex.message)
    return response


def set_error_handler(app):
    for code in exceptions.default_exceptions.keys():
        app.error_handler_spec[None][code] = error_json_handler


def manage_exceptions(e):
    if isinstance(e, exceptions.UserCredentialsException):
        return make_json_response(401, e.message)
    if isinstance(e, exceptions.ParseException):
        return make_json_response(400, e.message)
    if isinstance(e, exceptions.BDockerException):
        return make_json_response(e.code, e.message)
    return make_json_response(500, e.message)
