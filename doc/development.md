# Development Guide

Bdocker provides two daemons one for the working node and another one for the accounting node. They are implemented as
in RESTFUL APIs.

## Accounting REST API


The accounting API deploys a daemon in the accounting node, which will
listen the working node daemos and store the accouting information provided
from them.

More documentation will be provided soon.

##Working Node REST API

The working_node API deploys a daemon in the working nodes, which will
control the jobs configures under the bdocker environment.

More documentation will be provided soon.

## Modules

Bdocker has modular design. Three different modules

### Credentials module

This module manages the authentication and authorization by using tokens. It controls client privileges to access to 
docker containers, host directories and administrator tasks (such as configure, clean and notify functionalities).
It is important that the token file store **MUST be protected under root permissions**.
The main authorization rules are:
1. Containers can be only accesses by their owners.
2. Users can only access to documents that are inside their ``HOME``.
3. Only root users can execute administration tasks such *configure*, *clean* and *notify accounting*. 


### Batch module

This module is in charge of manage

## Extensiblity

Bdocker can be extended by adding new modules. 

### Batch module

A full support for extending Bdocker with new batch module drivers is provided.

### Credentials module

In the current version, the credentials module extensibility is limited, because it is dependent on the
token authentication. Thus, it can be extended with new drivers but always following the token mechanism.


