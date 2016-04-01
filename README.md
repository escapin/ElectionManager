# Election Manager

An Election Manager for sElect.  It allows to create, customize, and
remove **secure** and **verifiable** elections powered by sElect.


## Dependencies

* node.js and npm (tested on v4.3.1 and 1.4.21, respectively)
* python (tested on v.2.7.6)
* nginx (tested on v1.9.10)
* git and wget (only for downloading the proper files)
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
(*not responding* indicates a problem communicating with the server outputting
the election result).


## Usage

The web interface contains the following options to manage elections:

**Create Election** allows to create customized elections: Elements
such as title, description, starting/ending time, question, and 
list of choices can be set. Moreover, two more options can be selected:

* _Publish list of voters_: This option shows the email addresses of
  the voters who have voted in this election (but not what they have voted
  for), once the election is closed.
 
* _User providing verification code_: The voter will provide part of 
  the verification code to check whether her vote has been properly 
  counted. In this way, not even the voting booth needs to be trusted. 

**Set up Mock Election** creates a mock election with predetermined settings
(such as title, question, list of choices, and so on), which started one day ago
and will end in two days. In this setting, some mock voters already casted their ballots.

**Close Election** closes the selected election. It requires password 
confirmation, if one was set.

**Remove Election** removes the selected election. If the election result
needs to be saved on the server, the election must be closed first.
It requires password confirmation, if one was set.


A) When the election is open, **Invite Voters to Vote** shows a link to the voting booth of the selected election,
in order to allow eligible voters to cast their ballots.

B) Once the election is closed, **Check Election Result** shows a link to the _same_ voting booth used by the voters
to cast their ballot, in order to allow them to check the election result. 
This act triggers the *fully automated verification* procedure to investigate whether
the voter's choice has been actually counted.


## Development Environment

The development environment can be created with

```
make devenv
```

It creates a locally runnable configuration for the
web interface, it downloads the sElect system and creates the
development environment for it. This operation can be reverted by
`make devclean`.


The election manager and the nginx sessions used to handle the elections created can be started by:

```
./run.sh
```

When starting the server for the first time, the user will be prompted
to enter the administrator password used to manage any election (even
those one protected by a different password).


##### It is now possible to access the election manager by typing ``localhost:8443`` in the address bar of a browser.


The nginx sessions created can be stopped by

```
./stopNginx.sh
```

### Notes

Since the system is designed to run on https, running the system 
on http allows the transmission of passwords as plaintext.
