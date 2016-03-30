# Deployment

## How to deploy the Election Manager at `localhost`

After creating the development environment in the folder
`ElectionManager` (with `make devenv`) and configuring all the configuration
files to the desired settings, create the deployment environment with

```
make depenv
```

It set up all the files and folders to deploy the system at `localhost`.
This operation can be reverted by `make depclean`.


## How to run the Election Manager at `localhost`


The election manager and the nginx sessions to handle the election created can be started by:

```
./run.sh
```
This script requires root privileges to redirect the traffic from port 80.



**It is now possible to access the election manager via a browser typing ``localhost`` in the address bar.**

The nginx sessions created can be stopped by

```
./stopNginx.sh
```
The script requires root privileges, too.
