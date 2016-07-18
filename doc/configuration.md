#Configuration

##Daemon configuration

Bdocker provides two daemons one for the working node and another one for the accounting node. They are implemented as
in RESTFUL APIs. The daemons are configured by using a configuration file, the administrator has to configure this
file in the environment variable ``BDOCKER_CONF_FILE``. If it is not configured the system looks for the file in
``/etc/configure_bdocker.cfg``. In the following, we can a example of configuration of both daemons.

###Working Node


Every working node configures the following fields::

    [resource]
    # role can be working or accounting
    role = working

    [server]
    host = http://localhost
    port = 5000
    environ = debug
    workers = 2
    time_out = 200

    [accounting_server]
    host = http://localhost
    port = 5002

    [batch]
    # system can be: SGE, ...(add more modules)
    system = SGE
    enable_cgroups = True
    cgroups_dir = /sys/fs/cgroup
    parent_cgroup = /user

    [credentials]
    token_store = /etc/token_store.yml
    token_client_file = .bdocker_token

    [dockerAPI]
    base_url = unix://var/run/docker.sock

###Accounting

The accounting node configures the following fields::

    [resource]
    # role can be working or accounting
    role = accounting

    [server]
    host = http://localhost
    port = 5002
    environ = debug
    workers = 2
    time_out = 200

    [batch]
    # system can be: SGE, ...(add more modules)
    system = SGE
    bdocker_accounting=/home/jorge/bdocker_accounting

    [credentials]
    token_store = /etc/token_store.yml

###Configuration content


| Group             |Field               |Description                                |
| ----------------- |:------------------:|:------------------------------------------------|
|``server``         |                    |RESTFUL API access configuration                  
|                   |``host``            |Host (IP or hostname) in which the service will be provided.
|                   |``port``            |Port in which the service will be provided
|                   |``workers``         |Middleware multi-threads. It is 2 threads by default.
|                   |``timeout``         |Middleware requests timeout. It is 200 seconds by default.
|                   |``environ``         |Run mode for RESTFUL API. Middleware does not support it.
|                   |                     |It could be: debug, public, private.
|                   |                     |In case of public, the service will listen from  
|                  |                      |all the local IPs, it will use 0.0.0.0 IP.          
|``accounting_server``|                  |Configures in the WN the location of the          
|                   |                     |accounting service.                               
|                     |``host``          |Host in which the service is located. Format: ``http(s)://xx``              
|                     |``port``          |Port in which the service is located              
|``batch``        |                      |Batch system configuration                        
|                 |``system``            |Specify the type of resource manager              
|                 |``enable_cgroups``    |Enable cgroup accounting management.              
|                 |``cgroups_dir``       |CGroup root directory. By default:                
|                 |                      |"/sys/fs/cgroup"                                    
|                 |``parent_cgroup``     |Cgroup parent group: By default: "/"
|                 |``bdocker_accounting``|Accountig file for bdocker jobs.
|``credentials``  |                      |Credential module configuration
|                 |``token_store``       |File in which the tokens are store (root rights)
|                 |``token_client_file`` |Token file name. By default: ".bdocker_token".
|                 |                      |In configuration process, the user token is stored
|                 |                      |in the user home directory by using
|                 |                      |the name: $HOME/``token_client_file``_$JOB_ID.
|``dockerAPI``    |                      |
|                 | ``base_url``         |Docker server url. It could be a http link
|                 |                      |or a socket link (unix://var/run/docker.sock)

The parameter ``time_out`` is important for syncorinized long docker executions, since the server will
reset the request in case it exceed this time.
The working node daemon raise this exception in case this time is exceeded:
    [2016-07-18 14:06:44 +0000] [21197] [CRITICAL] WORKER TIMEOUT (pid:21206)


##Client configuration

 The client is configures by using the WN configuration file described above. It uses just the
 following fields:

###User configuration

    
|Group           |Field                |Description
| -------------- |:-------------------:|:------------------------------------------------|
|``server``      |                     |RESTFUL API access configuration
|                |``host``             |Host (IP or hostname) in which the service is located.
|                |``port``             |Port in which the service is located
|``credentials`` |                     |Credential module configuration
|                |``token_store``      |File in which the tokens are stored (root rights).
|                |                     |The client will use the administation token to
|                |                     |execute configuration and cleaning tasks.


##Bacth environment configuration

The configuration file is located in /etc/configure_bdocker.cfg by default. But it can be modified
by setting the environment variable ``BDOCKER_CONF_FILE``.

###Prolog::

    ################
    ### BDOCKER ####
    ################
    ## For JOB_ID with value 1
    ## The tocken will store the file in $HOME/.bdocker_token_1
    export BDOCKER_CONF_FILE="/etc/configure_bdocker.cfg"
    bdocker configure

###Epilog::

    ################
    ### BDOCKER ####
    ################
    ## For JOB_ID with value 1
    ## It will take the tocken from token in $HOME/.bdocker_token_1
    export BDOCKER_CONF_FILE="/etc/configure_bdocker.cfg"
    bdocker clean
