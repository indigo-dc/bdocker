# Installation

## Instalation from pip

At the moment the only way to install Bdocker is by using pip as local repository, we will provide a better
solution soon.
    ```
    $pip install .
    ```
# Deployment

Bdocker RESTFUL APIs are based on [Flask](flask.pocoo.org), but it does not support multi-request, so it can attend
just one request at the time. Thus, Bdocker middleware is managed by [gunicorn](http://gunicorn.org/)
which provides a multi-thread solution able to manage several request at the same time.

The daemons can be deployed by using the RESFUL APIs or the middleware solutions. On the other hand, the administrator
can use any other tool to deploy it.

## Deploy daemons based on the middleware solutions:

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

## Deploy daemons based on the RestFul APIs:

Both working node and accounting daemons can be directly launched from the RestFul APIs. This is not recommended for
a production environment, since it does not provide enough performance to control a batch system.
You can run the daemon as follows:

1. Run working node API:
    ```
    $python bdocker/api/working_node.py
    ```
2. Run accounting node API:
    ```
    $python bdocker/api/accounting.py
    ```
