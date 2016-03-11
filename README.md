# ElectionManager
An Election Manager for sElect.

## Dependencies

* node.js and npm.
* python
* nginx
* wget (used in the makefiles for getting the proper libraries).
* further dependencies needed for the sElect system:
  * Java JDK (tested with both openjdk-7 and oraclejdk-8).
  * Java Cryptography Extension (only for oraclejdk).

The system has been developed and deployed on Ubuntu Server 14.04.2 LTS.

## The Design

The project provides a web interface, which allows easy creations 
and management of customized elections, using the sElect system
(https://github.com/escapin/sElect.git) on a single server instance.

**Web Interface:** The webpage will display all elections in a table,
which have been set up. The table will show a unique ID to identify 
the election, the title given, when the election will start and end,
and the status of the election:  
*ready* - the election is currently 
running and eligible voters can cast their votes,  
*closed* - the election has ended and the results can be viewed,  
*not responding* - there is an error communicating with the server.  
The buttons to interact with the elections are described below.

**Create Election:** This button will create a simple election with 
predetermined properties (such as title, and description), which will 
start immediatly and end after 10 minutes.

**Vote:** After selecting an election (click on the election displayed 
in the table) this button will redirect you to another webpage to start 
the voting procedure (VotingBooth in the sElect system).

**Close:** The selected election will be closed, which requires password 
confirmation if one has been set.

**Remove Election:** Removes the selected election from the table. If 
the voting results should be saved on the server, the election has to 
be closed first.

**Advanced Election:** This will show an advanced settings page where a 
customized election can be created - such as title, description, 
starting-/ending time, questions and answers.

* **Publish list of voters:** Enabling this checkbox will show the all
  the e-mail addresses that have voted in this election (not what they
  have voted for), once the election is closed.
 
* **User providing verification code:** The user will provide part of 
  the verification code to check wether his vote has been properly 
  counted.
 
## Security Properties

The system is designed to be run on https, therefore running the system 
online on http would allow the interception of transmitted passwords.

## Developent Environment

## Development Environment

The development environment can be created with

```
make devenv
```
This creates a locally runnable configuration for the webinterface as
well as download the sElect project from https://github.com/escapin/sElect.git
and create the development environment for it. The created files can be removed 
by `make devclean`. 
