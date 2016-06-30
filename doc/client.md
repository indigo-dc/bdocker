Client Usage
=============

This document describes the commands available in Bdocker.

Administration
**************

There are several commands that have administration role. They need to be
execute before and after the utilization of bdocker by the root user.

Configure
---------
Configure the user credentials and the batch environment::

    bdocker configure
 
Clean
-----
Clean the user credentials and the batch environment::
Optional parameter to execute the action over another user token.

    bdocker [--token=XX] clean

User commands
*************
These commands are working over a specific user work area. The commands
need to be authorized by server through the user token. Such token
contains the user information and the containers that the user has.
By default the commands use the token stored in
$HOME/bdocker_token_$JOB_ID.

Pull
----
Pull a image (like ``docker pull``):
Parameters:
* image repository
Optional parameters:
* --token=XX or -t: Execute the action over another user token.

    bdocker pull [--token=XX] <repository>
 
List
-----
List all containers of the user (like ``docker ps``).
Optional parameters:
* --token=XX or -t: Execute the action over another user token.
* --all or -a: Show also the non-running containers

    bdocker ps [--token=XX] [--all]

Logs
----
Show the logs of a container (like ``docker logs``).
Parameters:
* Container id
Optional parameters:
* --token=XX or -t: Execute the action over another user token.

    bdocker logs [--token=XX] <container_id>

Inspect
-------
Show the information about a container (like ``docker inspect``).
Parameters:
* Container id
Optional parameters:
* --token=XX or -t: Execute the action over another user token.

    bdocker inspect [--token=XX] <container_id>

Delete
------
Delete one or serveral containers from a user (like ``docker rm``).
Parameters:
* Container id
Optional parameters:
* --token=XX or -t: Execute the action over another user token.

    bdocker rm [--token=XX] <container_id, container_id,...>

Copy
------
Copy files/folders between a container and the local filesystem
(like ``docker cp``).
Parameters:
* Container identification with the container path (id:/path)
* Host path (/path)
Optional parameters:
* --token=XX or -t: Execute the action over another user token.

    bdocker cp [--token=XX] <container_id:/path> </host/path>
    bdocker cp [--token=XX] </host/path> <container_id:/path>

Run
------
Creates a writeable container layer over the specified image,
and executes the command (like ``docker run``).
Parameters:
* Image identification
* Command

Optional parameters:
* --token=XX or -t: Execute the action over another user token.
* --detach or -d: Run container in background and print container ID.
* --working=XX or -w: Working directory inside the container.
* --volume=XX or -v : Bind mount a volume (/container_path/:/host_path)

    bdocker run [OPTIONS] <image_id> <command>
    
Examples
********
In the folowing we include several examples:

Run
---
Run over binding directory from the host::

    bdocker run -d 2fa927b5cdd3 -v /home/jorge/FAKE_JOB/:/tmp -w /tmp './script.sh'
    
