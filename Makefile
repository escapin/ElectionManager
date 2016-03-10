default:
	@echo Specify the goal: devenv OR devclean

devenv: nginxConf electionHandler sElect

nginxConf:
	mkdir -p nginx_config/handler/log
	mkdir -p nginx_config/root/log
	cp templates/nginx_root.conf nginx_config/root/nginx_root.conf
	cp templates/nginx_select.conf nginx_config/handler/nginx_select.conf
	python configNginx.py

electionHandler:
	cd ElectionHandler ; npm install
	cp templates/ElectionConfigFile.json ./ElectionConfigFile.json
	mkdir -p ElectionHandler/_data_
	mkdir -p elections

sElect:
	git clone https://github.com/escapin/sElect.git
	cd sElect; make devenv
	cp templates/config2js.js sElect/tools/config2js.js
	cp templates/refreshConfig.sh sElect/VotingBooth/refreshConfig.sh

devclean:
	-rm -r nginx_config
	-rm -r ElectionHandler/node_modules
	-rm -r ElectionHandler/_data_
	-rm ElectionConfigFile.json
	-rm ElectionHandler/webapp/js/ElectionConfigFile.js
	-rm ElectionHandler/webapp/js/config.js
	-rm -rf sElect/


