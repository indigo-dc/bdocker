# Configuration

In this document the configuration of the three components provided by Bdocker is described. Those three components are:
a. Working node daemon.
b. Accounting node daemon.
c. Command line client.
In Section 1, we explain the configuration of both daemons and describe the possible parameters. In Section 2, we describe
the configuration of the command line client. Last, Section 3 describes the configuration of the batch system environment,
which is made by using the epilog and prolog functionalities.

## 1. Daemon configuration

Bdocker provides two daemons one for the working node and another one for the accounting node. They are implemented as
RESTFUL APIs. The daemons are configured by using a configuration file, the administrator has to set this
file in the environment variable ``BDOCKER_CONF_FILE``. If that variable is not configured, the system uses by default
the file in ``/etc/configure_bdocker.cfg``. In the following, examples of configuration of both daemons are provided:

### Working Node


The working node configures the following fields:


    [resource]
    # role can be working or accounting
    role = working

    [server]
    host = http://localhost
    port = 5000
    logging = ERROR
    workers = 2
    time_out = 200

    [batch]
    # controller can be: SGEWNController (add more modules)
    controller = SGEWNController
    enable_cgroups = True
    cgroups_dir = /sys/fs/cgroup
    parent_cgroup = /user
    accounting_endpoint = http://localhost:5002
    include_wallclock = True
    only_docker_accounting = True

    [credentials]
    controller = TokenController
    token_store = /etc/token_store.yml
    token_client_file = .bdocker_token

    [dockerAPI]
    base_url = unix://var/run/docker.sock

### Accounting

The accounting configures the following fields:


    [resource]
    # role can be working or accounting
    role = accounting

    [server]
    host = http://localhost
    port = 5002
    logging = DEBUG
    workers = 2
    time_out = 200

    [batch]
    # controller can be: SGEAccountingController (add more modules)
    controller = SGEAccountingController
    bdocker_accounting=/home/jorge/bdocker_accounting

    [credentials]
    controller = TokenController
    token_store = /etc/token_store.yml


### Configuration parameters

The following table describes the possible configuration fields. Note that some of them are only required
 for some components (working or accounting).

| Group             |Field               |Description                                |
| ----------------- |:------------------:|:------------------------------------------------|
|``resource``       |                    |*Kind of resource*
|                   |``role``            |Daemon role, it can be ``working`` or ``accounting``.
|                   |                    |It configures the working node or accounting daemon.
|``server``         |                    |*RESTFUL API access configuration*                  
|                   |``host``            |Host (IP or hostname) in which the service will be provided.
|                   |``port``            |Port in which the service will be provided
|                   |``workers``         |Number of threads of the middleware. It is 2 threads by default. It must be equal or higher than 2.
|                   |``timeout``         |Middleware request timeout. It is 200 seconds by default.
|                   |``logging``         |Configure the logging level of bdocker. It can be set to the standard logging levels of python:
|                   |                     |ERROR, WARNING, INFO or DEBUG. By default it is ERROR.      
|                 |``logging_file``      |Configure the logging file. By default it is /var/log/bdocker.log.
|``batch``        |                      |*Batch system configuration*                        
|                 |``controller``        |Specify the class to manage the batch system.
|                 |                      |It can be for working nodes: ``SGEWNController`` (more controllers will be implemented)
|                 |                      |It can be for accounting nodes: ``SGEAccountingController`` (more controllers will be implemented)
|``credentials``  |                      |*Credential module configuration*
|                 |``controller``        |Specify the class to manage the user credentials.
|                 |                      |The only controller implemented is ``UserCredentials``
|                 |``token_store``       |File in which tokens are store (root rights). **It MUST be protected under root permissions**.
|``dockerAPI``    |(only working daemon) |*Docker access configuration*
|                 | ``base_url``         |Docker server url. It could be a http link or a socket link (unix://var/run/docker.sock)

The parameter ``time_out`` is important for synchronizing long docker executions, since the server will
reset the request in case it exceed this time.
The working node daemon raise this exception in case this time is exceeded:

``[2016-07-18 14:06:44 +0000] [21197] [CRITICAL] WORKER TIMEOUT (pid:21206)``

 In addition, we describe the configuration parameters related to the **Cgroup controller**, so that,
 any controller, which inherits from the CgroupWNController class, includes these parameters in the *batch* configuration group:

| Daemon            |Field               |Description                                |
| ----------------- |:------------------:|:------------------------------------------------|
|    working     |``enable_cgroups``    |Enable cgroup accounting management. By default is 'no' [true, false, yes, no].          
|    working     |``cgroups_dir``       |CGroup root directory. By default: "/sys/fs/cgroup"
|    working     |``parent_cgroup``     |Cgroup parent group: By default: "/"
|    working     |``accounting_endpoint``|Endpoint of the accounting server: Format: ``http(s)://host:port``
|    working     |``only_docker_accounting``|Store just the accounting related to the containers in the file, it avoids the rest of the
|                |                      |job processes. **But it always monitors the total time** for controlling the quota limits.
|                |                      |By default is 'yes' [true, false, yes, no].   
|  working      |``monitoring_time``   |Interval time between accounting iterations. In every iteration, it monitors accounting and copies the data to a file. By default: 10.
| accounting     |``bdocker_accounting``|Bdocker accounting file. By default: "/etc/bdocker_accounting".

**SGE batch controller** inherits from Cgroups controller, thus requires its configuration parameters. In addition
SGE batch controller allows to configure the wallclock time monitoring:

| Daemon            |Field               |Description                                |
| ----------------- |:--------------------:|:------------------------------------------------|
|    working     |``default_ru_wallclock`` | Default value for ru_wallclock accounting, By default: 0.
|    working     |``include_wallclock``    | Include the ru_wallclock time in the accounting, by default it is 'no' and
|                 |                      |the system includes the default_run_wallclock value. [true, false, yes, no]



## 2. Client configuration

In the current version, the client is deployed together to the working node, so that, it is configured by using the same configuration file.
However, the client just uses some of the configuration parameters (described in the previous section):

|Group           |Field                |Description
| -------------- |:-------------------:|:------------------------------------------------|
|``resource``    |                    |
|                |``role``            |It should be ``working`` for the client command line.
|``server``      |                     |RESTFUL API access configuration
|                |``host``             |Host (IP or hostname) in which the service is located.
|                |``port``             |Port in which the service is located
|                |``logging``         |Configure the logging level of bdocker.
|                |``logging_file``         |Configure the logging file. By default: /var/log/bdocker.log.
|``batch``        |                      |*Batch system configuration*. It provides the job information.      
|                 |``controller``        |Specify the class to manage the batch system.
|``credentials`` |                     |*Credential module configuration*
|                |``controller``        |Specify the class to manage the user credentials.
|                |``token_store``      |File in which the tokens are stored. **It MUST be protected under root permissions**.
|                |                     |The client will use the administrator token to execute configuration and cleaning tasks.
|                |``token_client_file`` |Token file name. By default: ".bdocker_token".
|                |                      |In the configuration process, the user token is stored in the user home directory by using
|                |                      |the path: $HOME/``token_client_file``_$JOB_ID.
|``dockerAPI``    |(only working daemon) |*Docker access configuration*
|                 | ``base_url``         |Docker server url. It could be a http link or a socket link (unix://var/run/docker.sock)


## 3. Batch environment configuration

The configuration file is located in ``/etc/configure_bdocker.cfg`` by default. But it can be modified
by setting the environment variable ``BDOCKER_CONF_FILE``.

Bdocker provide to commands that are executed before and after the utilization of bdocker by the root user.
First, we include the configure command in the prolog to configure the environment. Second, we include the clean
command, to clean the environment of bdocker job files, docker containers and other configurations.

### Prolog


    ################
    ### BDOCKER ####
    ################
    ## For JOB_ID with value 1
    ## The token will store the file in $HOME/.bdocker_token_1
    export BDOCKER_CONF_FILE="/etc/configure_bdocker.cfg"
    bdocker configure


### Epilog


    ################
    ### BDOCKER ####
    ################
    ## For JOB_ID with value 1
    ## It will take the tocken from token in $HOME/.bdocker_token_1
    export BDOCKER_CONF_FILE="/etc/configure_bdocker.cfg"
    bdocker clean

### Token store file

The credentials module requires this file to store the job information, every job is identified by using a
token. The tokens are created by the module during the configuration process and they are used for controlling
client privileges to access to docker container host directories.
In addition, the module uses an administration token, called ``admin``, to communicate the three components for administration tasks
(configure, clean and notify functionalities). So that, the token file **MUSTS CONTAIN THE FOLLOWING LINE**:

    admin: {token: <token_prolog>}

where <token_prolog> is the token configured by the admin, **it must be the same in all the components.**.

In order to have a proper security behaviour in bdocker, this file **must exists under root permissions**.
