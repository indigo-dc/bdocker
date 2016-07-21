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
    "log_name": "",
    "home": ""
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


pull_out = [
    '{"status":"Pulling from FAKE","id":"latest"}\r\n',
    '{"status":"Pulling fs layer","progressDetail":{},'
    '"id":"c2ddbea624bd"}',
    '{"status":"Pulling fs layer","progressDetail":{},'
    '"id":"f1e4b055fb65"}',
    '{"status":"Downloading","progressDetail":'
    '{"current":15876,"total":675993},"progress":'
    '"[=\\u003e] 15.88 kB/676 kB","id":"c2ddbea624bd"}',
    '{"status":"Downloading","progressDetail":'
    '{"current":32,"total":32},"progress":'
    '"[=================================================='
    '\\u003e]     32 B/32 B","id":"f1e4b055fb65"}',
    '{"status":"Extracting","progressDetail":'
    '{"current":32,"total":32},"progress":'
    '"[=======================================\\u003e]'
    '32 B/32 B","id":"f1e4b055fb65"}',
    '{"status":"Extracting","progressDetail":'
    '{"current":32,"total":32},'
    '"progress":"[===============\\u003e]'
    '32 B/32 B","id":"f1e4b055fb65"}',
    '{"status":"Pull complete","progressDetail":'
    '{},"id":"f1e4b055fb65"}',
    '{"status":"Digest: sha256:0326ccfeddaaa974a3de8a'
    '21db451e782a306a46d5c597eee743c91a93d36bb7"}\r\n',
    '{"status":"Status: Downloaded newer'
    ' image for busybox:latest"}\r\n']

pull_out_exist = [
    '{"status":"Pulling from FAKE","id":"latest"}\r\n',
    '{"status":"Pulling fs layer","progressDetail":{}'
    ',"id":"c2ddbea624bd"}',
    '{"status":"Pulling fs layer","progressDetail":{},'
    '"id":"f1e4b055fb65"}',
    '{"status":"Status: Image is up to date'
    ' for busybox:latest"}']

pull_out_error = [
    '{"errorDetail":"Error:'
    ' image library/busyb:latest not found"}\r\n'
]

fake_pull = {'imageOK': pull_out,
             'imageError': pull_out_error,
             'imageExist': pull_out_exist
             }

fake_containers = [uuid.uuid4().hex, uuid.uuid4().hex]
fake_images = [uuid.uuid4().hex, uuid.uuid4().hex]

fake_container_info = [
    {'Status': 'Exit (0) 1 day ago',
     'Id': fake_containers[0],
     'Command': 'ls',
     'Created': 1458301235,
     'Names': ['fakename'],
     'Image': fake_images[0],
     'Ports': [],
     },
    {'Status': 'Exit (0) 2 day ago',
     'Id': fake_containers[1],
     'Command': 'ls',
     'Created': 1458301230,
     'Names': ['fakename'],
     'Image': fake_images[0],
     'Ports': []}
]

fake_container_details = {
    'State':
        {'ExitCode': 0,
         'FinishedAt':
             '2015-08-24T11:02:05.902348909Z'
         },
    'Config':
        {'Image': 'fakeimage',
         'Hostname': 'fakehostname',
         'Cmd': ['fakecmd']},
    'Created':
        '2015-08-25T11:02:05.902348902Z',
    'Name': 'fakename',
    'NetworkSettings':
        {"Ports": 2}
}

container1 = {'Command': '/bin/sleep 30',
              'Created': 1412574844,
              'Id': '6e276c9e6e5759e12a6a9214efec6439f',
              'Image': 'busybox:buildroot-2014.02',
              'Names': ['/grave_mayer'],
              'Ports': [],
              'Status': 'Up 1 seconds'}

container2 = {'Command': 'whoami',
              'Created': 1412574844,
              'Id': '89034890sdfdjlksdf93k2390kldf',
              'Image': 'busybox:buildroot-2014.02',
              'Names': ['/grave_mayer'],
              'Ports': [],
              'Status': 'Up 1 seconds'}

container_real = [{'Status': 'Exited (0) 6 minutes ago',
                   'Created': 1458231723,
                   'Image': 'ubuntu', 'Labels': {},
                   'Ports': [], 'Command': 'sleep 30',
                   'Names': ['/nostalgic_noyce'],
                   'Id': 'f20b77988e436da8645cde68208'
                         '00dc9ee3aabe1bd9d2dd5b061a3c853ad688b'},
                  {'Status': 'Exited (0) 7 minutes ago',
                   'Created': 1458231670, 'Image': 'ubuntu',
                   'Labels': {}, 'Ports': [], 'Command': 'whoami',
                   'Names': ['/tender_nobel'],
                   'Id': '144a7e26743ed487217ae1494cac01197'
                         '245ef8e64669c666addd6a770639264'}]

fake_create = {'Id': uuid.uuid4(),
               'Warnings': None
               }
fake_log = ['root', 'home']


def create_generator(n):
    i = 0
    while i < n.__len__():
        yield n[i]
        i += 1

conf_sge = {
    'resource': {
        'role': "working"
    },
    'batch': {
        'controller': "SGEWNController",
        'accounting_endpoint': 'http://xx:88'
    },
    'server':
        {'host': 'host',
         'port': 'port',
         'logging': 'DEBUG'},
    'credentials':
        {'controller': "UserController",
         'token_store': "/fake",
         'token_client_file': 'token_file'},
    'dockerAPI': {
        'base_url': "xxx"
    },
}

job_env = ["algo", "/", "algo", "algo"]
