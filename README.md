INTRODUCTION
============

This sofware manages the execution of docker containers in  batch systems.
It provide two REST Full APIs that are designed for executing as daemons:
* The working_node API deploys a daemon in the working nodes, which will
control the jobs configures under the bdocker environment.
* The accounting API deploys a daemon in the accounting node, which will
 listen the working node daemos and store the accouting information provided
 from them.