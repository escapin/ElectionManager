# Election Manager deployment

## How to deploy the Election Manager at `localhost`

After creating the development environment in the folder
`ElectionManager` (with `make devenv`), in the folder
`ElectionManager/deployment' create the deployment environment with

```
make depenv
```

It set up all the files and folders to deploy the system at `localhost`.
This operation can be reverted by `make devclean`.


## How to run the Election Manager at `localhost`

1. In the folder `ElectionManager/deployment` start nginx by running

```
./startNginx.sh
```
This command requires root privileges.


2. In the folder `ElectionManager`, the election handler can be started
   by:

```
./run.sh
```

##### It is now possible to access the election manager via a browser typing ``localhost`` in the address bar.


3. When you stop the system, remember to stop all the nginx processes
   running

```
./stopNginx.sh
```
from the folder `ElectionManager/deployment`
(*not* the script in the folder `ElectionManager', which is only used
for the software development).  This command requires root privileges,
too.
