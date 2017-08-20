# Election Manager

An Election Manager for sElect.  It allows one to create, customize, and
remove **secure** and **verifiable** elections powered by sElect.


## Dependencies

* node.js and npm (tested on v6.11.2 and v3.10.10, respectively)
* python (tested on v.2.7.12)
* nginx (tested on v1.10)
* git and wget (only for downloading the proper files and library)
* Java JDK (tested on openjdk-9).


The system has been developed and deployed on Ubuntu Server 16.04.1 LTS.


## Design

The election manager provides a web interface allowing easy
creations and management of customized elections powered by the sElect
system (https://github.com/escapin/sElect.git) on a single server
instance.

The web interface displays a list of elections. Each election has an
unique ID, a given title, and a starting/ending time. Moreover, each
election is either *open* - the election is currently running and
eligible voters can cast their votes - or *closed* - the election is
over and the final result is ready and available (*not responding*
indicates a problem communicating with the server collecting the
ballots).


## Usage

The web interface contains the following options to manage elections:

**Create Election** allows one to create customized elections: Attributes 
such as title, description, starting/ending time, election question, 
and list of choices can be set. Moreover, two more options can be selected:

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
confirmation, if the password was set.

**Remove Election** removes the selected election. If the election result needs 
to be saved on the server, the election must have been previously closed. 
It requires password confirmation, if the password was set.

A) When the election is open, **Invite Voters to Vote** shows a link to the 
voting booth web-page. To allow eligible voters to cast their ballot, invite them 
to visit this web-page.

B) Once the election is closed, **Check Election Result** shows a link to the same 
voting booth web-page. To allow voters to check the election result, invite them to 
visit this web-page, namely the _same_ web-page they used to vote.


This act triggers the *fully automated verification* procedure to investigate whether the 
voter's choice has been actually counted.


## Create Fully Customized Election

Besides using the web interface, it is possible to create fully
customized election by providing a properly configured election manifest
and, optionally, a file containing a list of confidential voters which
only the Collecting Server has access to.  In the Election Manifest
provided, the URI and the public/private keys of the servers may not be
specified: these fields will anyway be overwritten with the proper
servers URI/cryptographic keys by the scripts creating the election.

In the `CustomizedElection` folder, a fully customized election can be created with

```
node createCustomizedElection.js -m <path/to/manifest.json> -p <pwdToCloseTheElection> [-v <path/to/confidentialVoters.json>] [-s <subdomain>] [-h] [-r]
```
where the parameters are
```
	-m <path/to/manifest.json>
	    Provide the election manifest file
	-p <pwdToCloseTheElection>
		Set password to close and remove the election to <pwdToCloseTheElection>
	-s <subdomain>
		Optional argument: instead of using the Election Lookup String (ELS) in the URI, the election will be displayed 
		at localhost:[port]/<subdomain> if the system run in localhost, <subdomain>.serverdomain otherwise.
	-v <path/to/confidentialVoters.json 
		Optional argument: instead of making the list of voters' email addresses publicly available in the election manifest, 
		provide them only to the collecting server.
	-h: 
		Optional argument: the election will be hidden from the ElectionHandler web interface, if any
	-r: 
		Optional argument: the user has to provide part of the verification code which will later be used to verify 
		that her vote has been properly counted. This would weaker the assumption on the voting booth's honesty.
```

In the `CustomizedElection` folder, a fully customized election can be removed with

```
node removeCustomizedElection.js -e <atLeast7charOfElectionID> -p <pwdInsertedWhenElectionCreated> [-h]
```
where the parameters are
```
	-e <atLeast7charOfElectionID>
	    The electionID of the election to be removed (at least 7 digits of the electionID are required)
	-p <pwdInsertedWhenElectionCreated>
	    The password inserted at creation time, which can also be used to close the election before the pre-set closing time
	-h 
	    Optional argument: the election to be removed is among the elections not shown in the election handler web interface, if any
	    (such elections are referred to as 'hidden elections').
	    If this argument is not provided, in case the election is not among the election displayed in the election handler, 
	    it will anyway check whether such an election is among the 'hidden elections'.
```

## Development Environment

The development environment can be created with

```
make devenv
```

It creates a locally runnable configuration for the
web interface, it downloads the sElect system and creates its
development environment. This operation can be reverted by
`make devclean`.


The election manager and the nginx sessions used to handle the elections 
created can be started by:

```
./run.sh
```

When starting the server for the first time, the user will be prompted
to enter the administrator password used to manage any election (even
those protected by an user-password).


##### It is now possible to access the election manager by typing ``localhost:8443`` in the address bar of a browser.


The nginx sessions created can be stopped by

```
./stopNginx.sh
```

### Notes

* At client side date and time are displayed in the user's machine 
  timezone, whereas at server side the UTC timezone is used.

* Using `CreateCustomElection` might interfere with an election created 
  by `server.js` if they are created at the same time.
