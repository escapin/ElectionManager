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
	if [ ! -d sElect]; then git clone -b merging https://github.com/escapin/sElect.git; fi
	cd sElect ; make devenv
	cp templates/config2js.js sElect/tools/config2js.js
	cp templates/refreshConfig.sh sElect/VotingBooth/refreshConfig.sh
	cd ElectionHandler ; npm install

devclean:
	-cd sElect ; make devclean
	-rm -r ElectionHandler/node_modules
	-rm -r ElectionHandler/_data_
	-rm -r nginx_config
	-rm ElectionConfigFile.json
	-rm ElectionHandler/webapp/js/ElectionConfigFile.js
	-rm ElectionHandler/webapp/js/config.js
	-rm sElect/tools/config2js.js
	-rm sElect/VotingBooth/refreshConfig.sh
	

test:
	cp templates/ElectionConfigFile.json ./ElectionConfigFile.json
	mkdir -p nginx_config/handler/log
	mkdir -p nginx_config/root/log
	-mkdir elections
	cp templates/nginx_root.conf nginx_config/root/nginx_root.conf
	cp templates/nginx_select.conf nginx_config/handler/nginx_select.conf
	mkdir ElectionHandler/_data_
	python configNginx.py

