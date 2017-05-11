# INTRODUCTION

This software manages the execution of docker containers in batch systems.
It provides two RESTFull APIs that are designed for executing as daemons:
* The working node API is deployed as daemon in working nodes.
 This daemon controls the execution of jobs which are configured under the bdocker environment.
* The accounting API is deployed as daemon in the accounting server.
This daemon listens the accounting request from the working node daemons and stores the accounting information
in the bdocker accounting file.

**This software is under testing**

[check out the bdocker EGI/INDIGO Conference 2017 poster here](http://www.lip.pt/~lalves/EGI-INDIGO2017.pdf)

