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

import copy
import os
import uuid

import mock

user_token = uuid.uuid4().hex
user_token_clean = uuid.uuid4().hex
user_token_delete = uuid.uuid4().hex
job_id = uuid.uuid4().hex
admin_token = uuid.uuid4().hex

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
    "prolog": {"token": admin_token },
    user_token: {
            "uid": uuid.uuid4().hex,
            "gid": uuid.uuid4().hex,
            "job": job_info,
            "home": "/boo",
            "containers": [uuid.uuid4().hex, uuid.uuid4().hex]
    },
    user_token_clean: {
            "uid": uuid.uuid4().hex,
            "gid": uuid.uuid4().hex,
            "job": job_info,
            "home": "/boo",
            "containers": [uuid.uuid4().hex, uuid.uuid4().hex]
    },
    user_token_delete: {
            "uid": uuid.uuid4().hex,
            "gid": uuid.uuid4().hex,
            "job": job_info,
            "home": "/boo",
            "containers": [uuid.uuid4().hex, uuid.uuid4().hex]
    }
}


def create_accounting_app():
        file_name = os.path.join(os.path.dirname(__file__),
                                 'sge_accounting_configure.cfg')
        token_store_acc = {
            "prolog": {"token": admin_token},
             user_token: {
                "uid": uuid.uuid4().hex,
                "gid": uuid.uuid4().hex,
                "home_dir": "/foo",
                "job": {
                    "id": uuid.uuid4().hex,
                    "spool": "/baa"}
            }}
        with mock.patch("bdocker.utils.read_yaml_file",
                        return_value=copy.deepcopy(token_store_acc)
                        ):
            with mock.patch("os.getenv",
                        return_value=file_name
                        ):
                from bdocker.api import accounting
                app = accounting.app
        return app


def create_job_info(job_id):
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
    return job_info


def create_working_node_app(file_name):
        with mock.patch("bdocker.utils.read_yaml_file",
                        return_value=copy.deepcopy(token_store)
                        ):
            with mock.patch("os.getenv",
                        return_value=file_name
                        ):
                from bdocker.api import working_node
                app = working_node.app
        return app