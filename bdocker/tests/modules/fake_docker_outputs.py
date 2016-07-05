import uuid

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

fake_create = {'Id': uuid.uuid4(),
               'Warnings': None
               }
fake_log = ['root', 'home']


def create_generator(n):
    i = 0
    while i < n.__len__():
        yield n[i]
        i += 1
