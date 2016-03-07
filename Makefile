# java libraries: version
#BCPROV_t=jdk15on
#BCPROV_v=1.51
BCPROV_t=jdk16
BCPROV_v=1.46
JUNIT_v=4.12
HARMCRESTCORE_v=1.3

default:
	@echo Specify the goal: devenv OR devclean OR cleanElection OR updateCryptoKeys OR prod

devenv: test
	cd sElect ; make devenv
	cd sElectRandom ; make devenv

devclean:
	cd sElect ; make devclean
	cd sElectRandom ; make devclean


test:
	mkdir -p nginx/handler/log
	mkdir -p nginx/root/log
	cp templates/nginx.conf nginx/root/nginx.conf
	cp templates/nginx_select.conf nginx/handler/nginx_select.conf
	mkdir ElectionHandler/_data_
	cp templates/pass.json ElectionHandler/_data_/pass.json
	python configNginx.py

