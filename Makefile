# java libraries: version
#BCPROV_t=jdk15on
#BCPROV_v=1.51
BCPROV_t=jdk16
BCPROV_v=1.46
JUNIT_v=4.12
HARMCRESTCORE_v=1.3

default:
	@echo Specify the goal: devenv OR devclean OR cleanElection OR updateCryptoKeys OR prod

devenv:
	cd sElect ; make devenv
	cd sElectRandom ; make devenv

devclean:
	cd sElect ; make devclean
	cd sElectRandom ; make devclean






