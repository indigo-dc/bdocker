# Configuration

In this document the configuration of the three component provided by Bdocker is described. The three components are:
1. Working node daemon.
2. Accounting node daemon.
3. Command line client.

## Daemon configuration

Bdocker provides two daemons one for the working node and another one for the accounting node. They are implemented as
RESTFUL APIs. The daemons are configured by using a configuration file, the administrator has to configure this
file in the environment variable ``BDOCKER_CONF_FILE``. If that variable is not configured, the system looks for
the file in ``/etc/configure_bdocker.cfg``. In the following, examples of configuration of both daemons are provided:

### Working Node


Every working node configures the following fields::

    [resource]
    # role can be working or accounting
    role = working

    [server]
    host = http://localhost
    port = 5000
    logging = ERROR
    workers = 2
    time_out = 200

    [accounting_server]
    host = http://localhost
    port = 5001

    [batch]
    # controller can be: SGEWNController, ...(add more modules)
    controller = SGEWNController
    enable_cgroups = True
    cgroups_dir = /sys/fs/cgroup
    parent_cgroup = /user
    accounting_endpoint = http://localhost:5002

    [credentials]
    controller = TokenController
    token_store = /etc/token_store.yml
    token_client_file = .bdocker_token

    [dockerAPI]
    base_url = unix://var/run/docker.sock

### Accounting

The accounting node configures the following fields::

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
    # controller can be: SGEAccountingController, ...(add more modules)
    controller = SGEAccountingController
    bdocker_accounting=/home/jorge/bdocker_accounting

    [credentials]
    controller = TokenController
    token_store = /etc/token_store.yml

### Configuration content

The following table describes the possible configuration fields. Note that some of them are only required
 for some components (working or accounting).

| Group             |Field               |Description                                |
| ----------------- |:------------------:|:------------------------------------------------|
|``resource``       |                    |**Kind of resource**
|                   |``role``            |Daemon role, it can be ``working`` or ``accounting``.
|                   |                    |It configures the working node or accounting daemon.
|``server``         |                    |**RESTFUL API access configuration**                  
|                   |``host``            |Host (IP or hostname) in which the service will be provided.
|                   |``port``            |Port in which the service will be provided
|                   |``workers``         |Number of middleware threads. It is 2 threads by default. It must be equal or higher than 2.
|                   |``timeout``         |Middleware requests timeout. It is 200 seconds by default.
|                   |``logging``         |Configure the logging level of bdocker. It can be set to the standard logging levels of python:
|                   |                     |ERROR, WARNING, INFO or DEBUG. By default it is ERROR.           
|``batch``        |                      |*Batch system configuration*                        
|                 |``controller``        |Specify the class to manage the batch system.
|                 |                      |It can be for working nodes: ``SGEController`` (more will be implemented)
|                 |                      |It can be for accounting nodes: ``SGEAccountingController`` (more will be implemented)
|  (only working) |``enable_cgroups``    |Enable cgroup accounting management. By default is False.          
|  (only working) |``cgroups_dir``       |CGroup root directory. By default: "/sys/fs/cgroup"
|  (only working) |``parent_cgroup``     |Cgroup parent group: By default: "/"
|  (only working) |``accounting_endpoint``|Configures in the WN the location of the accounting server: Format: ``http(s)://host:port``
|(only accounting)|``monitoring_time``   |Interval time for accounting monitoring and coping accounting to a file.
|(only accounting)|``bdocker_accounting``|Accounting file for bdocker jobs. By default: "/etc/bdocker_accounting"
|``credentials``  |                      |**Credential module configuration**
|                 |``controller``        |Specify the class to manage the user credentials.
|                 |                      |The only contoller implemented is ``UserCredentials``
|                 |``token_store``       |File in which the tokens are store (root rights). **It MUST be protected under root permissions**.
|``dockerAPI``    |  (only working)      |**Docker access configuration**
|                 | ``base_url``         |Docker server url. It could be a http link
|                 |                      |or a socket link (unix://var/run/docker.sock)

The parameter ``time_out`` is important for syncorinized long docker executions, since the server will
reset the request in case it exceed this time.
The working node daemon raise this exception in case this time is exceeded:

``[2016-07-18 14:06:44 +0000] [21197] [CRITICAL] WORKER TIMEOUT (pid:21206)``


## Client configuration

The client command line tool is configured by using the same configuration file. So that, in case it is
the working daemon environment, it is configured with its configuration. Although the client uses
the next configuration fields:
    
|Group           |Field                |Description
| -------------- |:-------------------:|:------------------------------------------------|
|``resource``    |                    |
|                |``role``            |It should be ``working`` for the client command line.
|``server``      |                     |RESTFUL API access configuration
|                |``host``             |Host (IP or hostname) in which the service is located.
|                |``port``             |Port in which the service is located
|                |``logging``         |Configure the logging level of bdocker.
|``credentials`` |                     |Credential module configuration
|                |``controller``        |Specify the class to manage the user credentials.
|                |``token_store``      |File in which the tokens are stored. **It MUST be protected under root permissions**.
|                |                     |The client will use the administrator token to
|                |                     |execute configuration and cleaning tasks.
|                |``token_client_file`` |Token file name. By default: ".bdocker_token".
|                |                      |In configuration process, the user token is stored
|                |                      |in the user home directory by using
|                |                      |the name: $HOME/``token_client_file``_$JOB_ID.


## Bacth environment configuration

The configuration file is located in /etc/configure_bdocker.cfg by default. But it can be modified
by setting the environment variable ``BDOCKER_CONF_FILE``.

### Prolog

    ################
    ### BDOCKER ####
    ################
    ## For JOB_ID with value 1
    ## The tocken will store the file in $HOME/.bdocker_token_1
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
