#Client Usage


This document describes the commands available in Bdocker.

##Administration

There are several commands that have administration role. They need to be
execute before and after the utilization of bdocker by the root user.

###Configure

Configure the user credentials and the batch environment::

    bdocker configure
 
###Clean

Clean the user credentials and the batch environment::

    bdocker [--token=XX] clean
    
Optional parameters:
* --token=XX or -t XX: Execute the action over another user token.

##User commands

These commands are working over a specific user work area. The commands
need to be authorized by server through the user token. Such token
contains the user information and the containers that the user has.
By default the commands use the token stored in
$HOME/bdocker_token_$JOB_ID.

###Pull

Pull a image (like ``docker pull``)::

    bdocker pull [--token=XX] <repository>
    
Parameters:
* image repository
Optional parameters:
* --token=XX or -t XX: Execute the action over another user token.
 
###List

List all containers of the user (like ``docker ps``)::

    bdocker ps [--token=XX] [--all]
    
Optional parameters:
* --token=XX or -t: Execute the action over another user token.
* --all or -a: Show also the non-running containers

###Logs

Show the logs of a container (like ``docker logs``)::

    bdocker logs [--token=XX] <container_id>

Parameters:
* Container id
Optional parameters:
* --token=XX or -t XX: Execute the action over another user token.

###Inspect

Show the information about a container (like ``docker inspect``)::

    bdocker inspect [--token=XX] <container_id>

Parameters:
* Container id
Optional parameters:
* --token=XX or -t XX: Execute the action over another user token.

###Delete

Delete one or serveral containers from a user (like ``docker rm``)::

    bdocker rm [--token=XX] <container_id, container_id,...>
    
Parameters:
* Container id
Optional parameters:
* --token=XX or -t XX: Execute the action over another user token.

###Copy

Copy files/folders between a container and the local filesystem
(like ``docker cp``)::

    bdocker cp [--token=XX] <container_id:/path> </host/path>
    bdocker cp [--token=XX] </host/path> <container_id:/path>
    
Parameters:
* Container identification with the container path (id:/path)
* Host path (/path)
Optional parameters:
* --token=XX or -t XX: Execute the action over another user token.

###Run

Creates a writeable container layer over the specified image,
and executes the command (like ``docker run``)::

    bdocker run [OPTIONS] <image_id> <command>

Parameters:
* Image identification
* Command

Optional parameters:
* --token=XX or -t XX: Execute the action over another user token.
* --detach or -d: Run container in background and print container ID.
* --workdir=XX or -w XX: Working directory inside the container.
* --volume=XX or -v XX: Bind mount a volume (/container_path/:/host_path)

    
##Examples

In the folowing we include several examples:

###Run

Run over binding directory from the host::

    bdocker run -d 2fa927b5cdd3 -v /home/jorge/FAKE_JOB/:/tmp -w /tmp './script.sh'

###Copy


Copy from host to container::

    bdocker cp /home/jorge/folder ec1dacd765197f2b63230875e388906e4ed6958c6ac71e57de8345c5f7560d54:/tmp/to_container

Copy from container to host::

    bdocker cp ec1dacd765197f2b63230875e388906e4ed6958c6ac71e57de8345c5f7560d54:/tmp/folder /home/jorge/

  

