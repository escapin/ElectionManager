# java libraries: version
#BCPROV_t=jdk15on
#BCPROV_v=1.51
BCPROV_t=jdk16
BCPROV_v=1.46
JUNIT_v=4.12
HARMCRESTCORE_v=1.3

default:
	@echo Specify the goal: devenv OR devclean

devenv: test
	git clone -b merging https://github.com/escapin/sElect.git
	cd sElect ; make devenv
	cp templates/config2js.js sElect/tools/config2js.js
	cp templates/refreshConfig.sh sElect/VotingBooth/refreshConfig.sh

devclean:
	cd sElect ; make devclean


test:
	cp templates/ElectionConfigFile.json ./ElectionConfigFile.json
	mkdir -p nginx_config/handler/log
	mkdir -p nginx_config/root/log
	cp templates/nginx.conf nginx_config/root/nginx.conf
	cp templates/nginx_select.conf nginx_config/handler/nginx_select.conf
	mkdir ElectionHandler/_data_
	cp templates/pass.json ElectionHandler/_data_/pass.json
	python configNginx.py

