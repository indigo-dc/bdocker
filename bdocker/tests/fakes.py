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
import uuid

import webob

user_token = uuid.uuid4().hex
user_token_clean = uuid.uuid4().hex
user_token_delete = uuid.uuid4().hex
user_token_no_container = uuid.uuid4().hex
user_token_no_images = uuid.uuid4().hex
job_id = uuid.uuid4().hex
admin_token = uuid.uuid4().hex
containers = [uuid.uuid4().hex,
              uuid.uuid4().hex]
images = [uuid.uuid4().hex]

job_info = {
    "job_id": job_id,
    "spool": "/baa",
    "max_cpu": 0,
    "max_memory": 0,
    "user_name": "",
    "queue_name": "",
    "host_name": "",
    "job_name": "",
    "account_name": "",
    "log_name": ""
}

token_store = {
    "prolog": {"token": admin_token},
    user_token: {
        "uid": uuid.uuid4().hex,
        "gid": uuid.uuid4().hex,
        "job": job_info,
        "images": images,
        "home": "/boo",
        "containers": containers
    },
    user_token_clean: {
        "uid": uuid.uuid4().hex,
        "gid": uuid.uuid4().hex,
        "job": job_info,
        "home": "/boo",
        "containers": containers
    },
    user_token_delete: {
        "uid": uuid.uuid4().hex,
        "gid": uuid.uuid4().hex,
        "job": job_info,
        "home": "/boo",
        "containers": containers
    },
    user_token_no_container: {
        "uid": uuid.uuid4().hex,
        "gid": uuid.uuid4().hex,
        "job": job_info,
        "images": images,
        "home": "/boo",
    },
    user_token_no_images: {
        "uid": uuid.uuid4().hex,
        "gid": uuid.uuid4().hex,
        "job": job_info,
        "home": "/boo",
    }
}


def create_job_info(job_ident):
    job_data = {
        "job_id": job_ident,
        "spool": "/baa",
        "max_cpu": 0,
        "max_memory": 0,
        "user_name": "",
        "queue_name": "",
        "host_name": "",
        "job_name": "",
        "account_name": "",
        "log_name": ""
    }
    return job_data


def create_usercrentials():
    parameters = {
        "token": "tokennnnnn",
        "user_credentials":
            {'uid': 'uuuuuuuuuuiiiidddddd',
             'gid': 'gggggggggguuuiiidd',
             'home': '/home',
             }
    }
    return parameters


def create_fake_json_resp(data, status=200):
    r = webob.Response()
    r.headers["Content-Type"] = "application/json"
    r.charset = "utf8"
    r.body = json.dumps(data).encode("utf8")
    r.status_code = status
    return r
