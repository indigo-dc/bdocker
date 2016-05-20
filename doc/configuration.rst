Configuration
=============

server configuration
********************

The server daemon is configured by using a configuration file, the administrator has to configure this file in the
environment variable ``BDOCKER_CONF_FILE``. If it is not configured the system looks for the file in
``/root/configure_bdocker.cfg``. The file has the following fields::

    [server]
    host = localhost
    port = 5000
    environ = debug

    [batch]
    # system can be: SGE, ...(add more modules)
    system = SGE

    [credentials]
    token_store = /root/token_store.yml

    [dockerAPI]
    base_url = localhost:2375

.. table:: Configuration content

    ================ ===================== =================================================
    Group             Field                 Description
    ================ ===================== =================================================
    ``server``                              Rest service access configuration
                      ``host``              Host in which the service will be provided
                      ``port``              Port in which the service will be provided
                      ``environ``           Run mode. It could be: debug, public, private.
                                            In case of public, the service will listen from
                                            all the local IPs, it will use 0.0.0.0 IP.

    ``batch``                               Batch system configuration
                      ``system``            Specify the type of resource manager

    ``credentials``                         Credential module configuration
                      ``token_store``       File in which the tokens are store (root rights)

    ``dockerAPI``
                      ``base_url``          Docker server url. It could be a http link
                                            or a socket link (unix://var/run/docker.sock)
    ================ ================== ====================================================

client configuration
********************

 The client needs to configure the following environment variables:

 =========================== ======================== =================================================
 Variable                     Default value            Description
 =========================== ======================== =================================================
 ``BDOCKER_ENDPOINT``         http://localhost:5000    Bdocker serve endpoint
 ``BDOCKER_TOKEN_STORE``      /root/token_store.yml    File in which the tokens are store (root rights)
 ``BDOCKER_USER_TOKEN_FILE``  .bdocker_token           Tokens are stored in $HOME/``.token_client_file``

BATCH configuration
********************

Epilog::

    #########
    ## BDOCKER
    # export BDOCKER_ENDPOINT=http://0.0.0.0:5000
    # export BDOCKER_TOKEN_STORE=...
    # user_id=`id -u`
    # job_id=$JOB_ID
    ## It will store the token in $HOME/.bdocker_token
    # bdocker -H $BDOCKER_ENDPOINT credentials $user_id $job_id
    #


