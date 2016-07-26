# Installation

## Instalation from pip

At the moment the only way to install Bdocker is by using pip as local repository, we will provide a better
solution soon.
    ```
    $pip install .
    ```
# Deployment

Bdocker RESTFUL APIs are based on [Flask](flask.pocoo.org), but it does not support multi-request, so it can attend
just one request at the same time. Thus, Bdocker middleware is managed by [gunicorn](http://gunicorn.org/)
which provides a multi-thread solution able to manage several requests at the same time.

The daemons can be deployed by using the RESFUL APIs or the middleware solutions. On the other hand, the administrator
can use any other tool to deploy it.

## Run daemons based on the middleware solutions:

The proper way to launch the daemons is by using the middleware. Those daemons provide multi-thread management able to
attend several request at the same time. In order to configure the middleware, the ``workers`` and ``timeout`` parameters
should be specified in the configuration file (see documentation about [configuration](doc/configuration.md)).
You can run the daemon as follows:

1. Run working node middleware:
    ```
    $python bdocker/middleware/working_node.py
    ```    
2. Run accounting node middleware:
    ```
    $python bdocker/middleware/accounting.py
    ```

## Run daemons based on the RestFul APIs:

Both working node and accounting daemons can be directly launched from the RestFul APIs. This is not recommended for
a production environment, since it does not provide enough performance to control a batch system.
You can run the APIs as follows:

1. Run working node API:
    ```
    $python bdocker/api/working_node.py
    ```
2. Run accounting node API:
    ```
    $python bdocker/api/accounting.py
    ```
    
## Deploy daemon as services:

We provide the information about how to deploy the bdocker daemons as services in Centos 7.

###Centos 7

In order to create the daemos as services in Centos 7, we follow the next steps:

1. Create systemd file:
  * For the working node daemon:
    ```
    [root@ge bdocker]# vi /lib/systemd/system/bdocker.service

    [Unit]
    Description=Bdocker daemon for controlling container execution in WN.
    After=multi-user.target
    
    [Service]
    Type=idle
    ExecStart=/usr/bin/python /usr/lib/python2.7/site-packages/bdocker/middleware/working_node.py 
    [Install]
    WantedBy=multi-user.target
    ```
  * For the accounting daemon:
    ```
    [root@ge bdocker]# vi /lib/systemd/system/bdocker.service

    [Unit]
    Description=Bdocker daemon for controlling container execution in the accounting server.
    After=multi-user.target
    
    [Service]
    Type=idle
    ExecStart=/usr/bin/python /usr/lib/python2.7/site-packages/bdocker/middleware/accounting.py 
    [Install]
    WantedBy=multi-user.target
    ```
            
2. Give permissions:
     ```
    [root@ge bdocker]# sudo chmod 644 /lib/systemd/system/bdocker.service
    ```
3. Reload systemd:
    ```
    [root@ge bdocker]# systemctl daemon-reload
    [root@ge bdocker]# systemctl enable bdocker.service
    Created symlink from /etc/systemd/system/multi-user.target.wants/bdocker.service to
    /usr/lib/systemd/system/bdocker.service.
    ```
4. Start the bdocker service:
    ```
    [root@ge bdocker]# service bdocker start
    Redirecting to /bin/systemctl start  bdocker.service
    ```    
5. Check status of the bdocker service:
    ```
    [root@ge bdocker]# service bdocker status
    Redirecting to /bin/systemctl status  bdocker.service
    bdocker.service - Bdocker daemon for controlling container execution in WN.
    Loaded: loaded (/usr/lib/systemd/system/bdocker.service; enabled; vendor preset: disabled)
    Active: active (running) since...
    ```