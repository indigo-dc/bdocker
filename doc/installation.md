# Installation

## Instalation from pip

At the moment the only way to install Bdocker is by using pip as local repository, we will provide a better
solution soon.
    ```
    $pip install .
    ```
# Deployment

Bdocker RESTFUL APIs are based on [Flask](flask.pocoo.org), but it does not support multi-request, it can attend
just one request at the time. So that, Bdocker middleware is manage by [gunicorn](http://gunicorn.org/)
which provide middleware multi-thread able to manage several request at the time (see the parameter ``workers``
 in the configuration documentation).

The daemons can be deployed by using directly by using the RESFUL APIs or using the middleware solutions. Furthermore,
the administration can use any other tool to deploy the APIs.

In addition, we plan to provide other deployment solutions.


## Deploy daemons based on the middleware solutions:

The proper way to launch the daemons is by using the middleware. Those daemons provide multi-thread management able to
attend several request at the time. In order to configure the middleware, the ``workers`` and ``timeout`` parameters should
be configured in the configuration file (see documentation about the configuration).
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
Both daemons, working node and accounting, can be launch directly from the RestFul APIs. Since the performance of
that is not enough to control a batch syste, it is only for testing purposes. You can run the daemon as follows:

1. Run working node API:
    ```
    $python bdocker/api/working_node.py
    ```
2. Run accounting node API:
    ```
    $python bdocker/api/accounting.py
    ```
