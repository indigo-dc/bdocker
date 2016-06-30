#INTRODUCTION

This sofware manages the execution of docker containers in  batch systems.
It provide two REST Full APIs that are designed for executing as daemons:
* The working_node API deploys a daemon in working nodes, which will
control the jobs configured under the bdocker environment.
* The accounting API deploys a daemon in the accounting node, which will
 listen the working node daemons and store the accounting information provided
 from them.