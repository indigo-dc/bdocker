# Development Guide

Bdocker provides two daemons one for the working node and another one for the accounting node. They are implemented as
in RESTFUL APIs.

## Working Node REST API

The working_node API deploys a daemon in the working nodes, which will
control the jobs configures under the bdocker environment.
More documentation will be provided soon. Meanwhile more details about the classes and methods can be found in the
internal documentation.

## Accounting REST API

The accounting API deploys a daemon in the accounting node, which will
listen the working node daemos and store the accounting information provided
from them.
More documentation will be provided soon. Meanwhile more details about the classes and methods can be found in the
internal documentation.

## Modules

Bdocker has modular design. Three different modules compose the system: credentials, batch, and docker modules.
In the following we describe the modules and its behaviour, more details about the classes and methods can be found in the
internal documentation.

### Credentials module

This module manages the authentication and authorization by using tokens. It controls client privileges to access to 
docker containers, host directories and administrator tasks (such as configure, clean and notify functionalities).
It is important that the token file store **MUST be protected under root permissions**.
The main authorization rules are:
1. Containers can be only accesses by their owners.
2. Users can only access to documents that are inside their ``HOME``.
3. Only root users can execute administration tasks such *configure*, *clean* and *notify accounting*. 

### Batch module

This module is in charge of preparing the batch system environment and controlling the job execution.
There are to kind of controllers in this module: working node and accounting controller.

#### Working node
The base class for controlling the working node is the WNController class, which does not implement any method. On the other hand,
WNController class is extended in the class CgroupWNController, which implements the methods to support the Cgroups management,
but it does not support any batch system management.

**The CgroupsWNController provides the following functionalities**:
1. Configuration method ``conf_environment``, which performs the following steps:
   * It creates the new cgroup tree (/sys/fs/cgroup/cpu/groupname/,  /sys/fs/cgroup/memory/groupname/, ...).
   * It writes the pid of the parent job to the cgroup tasks files. The children processes are automatically created in our cgroup.
2. Clean method ``clean_environment``: Delete the new cgroups.
3. Launch cgroups monitoring method ``launch_job_monitoring``, It tracks the CPU and memory accounting of such cgroup and
  store it in a local accounting file. If it exceeds the cuotas the job process is killed. 
4. Notify the accounting to the accounting node. It send a request within the accounting information as a string with
the proper batch system accounting format.

In the current version, the **SGE batch system is supported by using the SGEWNController class which**
inherits from CgroupController. In the following, the workflow of the job accounting management for SGE based in Cgroups:
* Prolog should run the configuration method ``conf_environment``, which performs the following steps:
  1. It creates the new cgroup tree.
  2. It writes the pid of the parent job to the cgroup tasks files. This pid is located in SGE_JOB_SPOOL_DIR/pid file.
  3. The rest of the processes are children of that pid (prolog, job and epilog), so they are automatically created in our cgroup.
  4. It launch a daemon to control the job accounting.
* Later, the 'bdocker run' command specifies our cgroup to the docker-py client. So the containers are also inside our cgroup.
* Epilog should run the clean method ``clean_environment``, it gets the cgroup information and delete the local file (containers are previously forced to stop by the docker module).

#### Accounting node
The base class for controlling the accounting node is the AccountingController, which does implement any method. This controller
is in charge of listening the working node daemons waiting for accounting notifications, the notification data is storage in
a file following the accounting format of each batch system.
In the current version, the SGE batch system is supported by using the SGEAccountingController class.

### Docker mudule
The docker module is in charge of managing the docker-py client for been used in the bdocker tool.

## Extensiblity

Bdocker can be extended by adding new controlers related to credentials and batch modules. 

### Batch module

A full support for extending Bdocker with new batch module drivers is provided. In order to implement a new
batch controller, these rules **MUST** be satisfy:
1. The new controller must be located in ``bdocker.modules.batch`` module.
2. The new class must inherit from the base class:
   * In case of Working node controller: ``bdocker.modules.batch.WNController``.
   * In case of Accounting node controller: ``bdocker.modules.batch.AccountingController``.
   * In case of you want to base your controller in Cgroups, it musts inherit from ``bdocker.modules.batch.CgroupsWNController``.
3. In order to use the new controller, the class name need to be configured in the bdocker configuration file.
4. The documentation about documentation must be updated, including the name of the new class.

### Credentials module

In the current version, the credentials module extensibility is limited, because it is dependent on the
token authentication. Thus, it can be extended with new drivers but always following the token mechanism.
In order to implement a new
batch controller, these rules **MUST** be satisfied:
1. The new controller must be located in ``bdocker.modules.credentials`` module.
2. The new class must inherited from the base class ``bdocker.modules.credentials.UserController``.
3. In order to use the new controller, the class name need to be configured in the bdocker configuration file.
4. The documentation about documentation must be updated, including the name of the new class.


