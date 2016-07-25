#INTRODUCTION

This software manages the execution of docker containers in  batch systems.
It provide two REST Full APIs that are designed for executing as daemons:
* The working node API is deployed as daemon in working nodes.
 This daemon controls the jobs execution which are configured under the bdocker environment.
* The accounting API is deployed as daemon in the accounting server.
This daemon listens the accounting request from the working node daemons and stores the accounting information
in the bdocker accounting file.