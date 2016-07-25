# Development Guide

Bdocker provides two daemons. First, the **working node daemon** daemon is in charge of managing the job execution in the 
the working node. Second, the **accounting daemon** listens the working nodes accounting communication and stores it in the
bdocker accounting file. They are implemented as in RESTFUL APIs.

## Working Node REST API

The working node API is deployed as daemon in working nodes. This daemon controls the jobs execution which are configured
under the bdocker environment. More details about the classes and methods can be found in the internal documentation.
In addition, we plan to provide more documentation soon.

## Accounting REST API

The accounting API is deployed as daemon in the accounting server. This daemon listens the accounting request from the 
working node daemons and stores the accounting information in the bdocker accounting file. More details about the classes
and methods can be found in the internal documentation.
In addition, we plan to provide more documentation soon.

## Modules

Bdocker has modular design. Three different modules compose the system: credentials, batch, and docker modules.
In the following we describe the modules and its behaviour. More details about the classes and methods can be found in the
internal documentation.

### Credentials module

This module manages the authentication and authorization by using tokens. It controls client privileges to access to 
docker containers, host directories and administration tasks (such as configure, clean and notify functionality).
The token file **MUST be protected under root permissions**.
The main authorization rules are:
1. Containers can be only accesses by their owners.
2. Users can only access to documents that are inside their ``HOME``.
3. Only root users can execute administration tasks such *configure*, *clean* and *notify accounting*. 

### Batch module

This module is in charge of preparing the batch system environment and controlling the job execution.
There are to kind of controllers in this module: working node and accounting controller.

#### Working node
The base class for controlling the working node is the WNController abstract class. On the other hand,
WNController class is extended in the class CgroupWNController, which implements methods to support the Cgroups management,
but it does not support any batch system management.

**The CgroupsWNController provides the following functionalities**:
1. Configuration method ``conf_environment`` performs the following steps:
   * It creates the new cgroup tree (/sys/fs/cgroup/cpu/groupname/,  /sys/fs/cgroup/memory/groupname/, ...).
   * It writes the pid of the parent job in the cgroup tasks files. Later, children processes are automatically created in our cgroup.
2. Clean method ``clean_environment``: Delete the new cgroups.
3. Monitoring method ``launch_job_monitoring``, tracks the CPU and memory accounting a given cgroup and
  store the information in a local accounting file. If it exceeds the user quotas, the job process is killed. 
4. Notify method ``notify_accounting``, sends a request within the accounting information as a string with
the proper batch system accounting format.

In the current version, the **SGE batch system is supported by using the SGEWNController class** which
inherits from CgroupController.
In the following, the workflow of the job accounting management for SGE based in Cgroups is described:
* Prolog should run the configuration method ``conf_environment``, which performs the following steps:
  1. It creates the *job cgroup* tree identified by using the job id.
    * In order to keep separated the job and the container accounting, it is created another cgroup for the job processes
    called *COMMON*. It is located inside the *job cgroup*. It allows to store all the job accounting or only the containers and
    avoid the job data which is already stored in the default SGE file.
  2. It writes the pid of the parent job to the *COMMON* cgroup tasks files. This pid is located in SGE_JOB_SPOOL_DIR/pid file.
  3. The rest of the job processes are children of that pid (prolog, job and epilog), so they are automatically created in the *COMMON* cgroup.
  4. It launches a subprocess to control the accounting.
* Later, the *bdocker run* command specifies the *job cgroup* when running docker-py client. So the containers are also
running inside our *job cgroup*.
* Epilog should run the cleaning method ``clean_environment``, it gets the cgroup information and
 delete the local accounting file (containers are previously forced to stop by the docker module).

#### Accounting node
The base class for controlling the accounting node is the AccountingController abstract class. This controller
is in charge of listening the working node daemons waiting for accounting notifications, the notification data is stored in
a file following the accounting format of each batch system.
In the current version, the SGE batch system is supported by using the SGEAccountingController class.

### Docker mudule
The docker module is in charge of managing the docker-py client for being used in the bdocker tool.

## Extensibility

Bdocker can be extended by adding new controllers related to credentials and batch modules. 

### Batch module

A full support for extending Bdocker with new batch module drivers is provided. In order to implement a new
batch controller, these rules **MUST** be satisfy:
1. The new controller musts be located in the ``bdocker.modules.batch`` module.
2. The new class musts inherit from the base class:
   * In case of Working node controller: ``bdocker.modules.batch.WNController``.
   * In case of Accounting node controller: ``bdocker.modules.batch.AccountingController``.
   * In case of you want to base your controller on Cgroups, it musts inherit from ``bdocker.modules.batch.CgroupsWNController``.
3. In order to use the new controller, the class name needs to be configured in the bdocker configuration file.
4. The documentation about it musts be updated.

### Credentials module

In the current version, the credentials module extensibility is limited, because it depends on the
token authentication. Thus, it can be extended with new drivers but always following the token mechanism.
In order to implement a new batch controller, these rules **MUST** be satisfied:
1. The new controller musts be located in the ``bdocker.modules.credentials`` module.
2. The new class musts inherit from the base class ``bdocker.modules.credentials.TokenController``.
3. In order to use the new controller, the class name needs to be configured in the bdocker configuration file.
4. The documentation about it musts be updated.


