# Election Manager

An Election Manager for sElect.  It allows to create, customize, and
remove **secure** and **verifiable** elections powered by sElect.


## Dependencies

* node.js and npm (tested on v4.3.1 and 1.4.21, respectively)
* python (tested on v.2.7)
* nginx (tested on v1.9.10)
* superuser privileges on the operative system
* git and wget
* further dependencies needed for the sElect system:
  * Java JDK (tested with both openjdk-7 and oraclejdk-8).
  * Java Cryptography Extension (only for oraclejdk).

The system has been developed and deployed on Ubuntu Server 14.04.2 LTS.


## Design

The election manager provides a web interface allowing easy
creations and management of customized elections powered by the sElect
system (https://github.com/escapin/sElect.git) on a single server
instance.

The web interface displays a list of elections. Each election has an
unique ID, a given title, and a starting/ending time. Moreover, each
election is either *open* - the election is currently running and
eligible voters can cast their votes -
or *closed* - the election is over and the final result is ready and available
(*not responding* indicates a problem communicating with the server).


## Usage 

The web interface contains the following options to manage elections:

**Create Election** creates a mock election with predetermined settings
(such as title, description, and so on), which starts immediately
and ends after 72 hours.

**Vote** redirects to the voting booth of the sElect system to start
the voting procedure (if the election is open).

**Close** closes the selected election. It requires password 
confirmation, if set.

**Remove Election** removes the selected election. If the voting results
should be saved on the server, the election has to be closed first.

**Advanced Election** shows the advanced settings to create customized
elections.  Elements such as title, description, starting/ending time,
questions and answers can be set. In particular:

* _Publish list of voters_: This option shows the e-mail addresses of
  the voters who have voted in this election (not what they have voted
  for), once the election is closed.
 
* _User providing verification code_: The user will provide part of 
  the verification code to check whether his vote has been properly 
  counted. In this way, not even the voting booth needs to be trusted. 
 
### Security Issues

Since the system is designed to run on https, running the system 
on http allows the transmission of passwords as plaintext.


## Development Environment

The development environment can be created with

```
make devenv
```

It creates a locally runnable configuration for the
web interface, it downloads the sElect system and creates the
development environment for it. This operation can be reverted by
`make devclean`.


The *nginx* HTTP server is configured to redirect the traffic from ports
80 and 433 to port 8443:

```
./setup_nginx.sh
```

This command requires [sudo] password since, by UNIX standard, only with
*superuser* privileges it is possible to listen to privilege ports
(i.e., ports below 1024).


The nginx sessions and the election manager server can be started by

```
./run.sh
```

When starting the server for the first time, the user will be prompted to enter
the administrator password which can be used to manage any election, even those one protected by a different password.

To access the election manager, open a browser and type  ``localhost``` in the URL.

The nginx process created above can be stopped by

```
./stop_nginx.sh
```

The user will be prompted for [sudo] password again, in order to
end the instance created by the superuser.

