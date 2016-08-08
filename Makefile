default:
	@echo Specify the goal: devenv OR devclean

devenv: handler custom nginx select


handler:
	cd ElectionHandler; make
	mkdir -p _configFiles_
	cp templates/config.json _configFiles_/handlerConfigFile.json
	mkdir -p elections

custom:
	cd CustomizedElection; npm install
	mkdir -p elections_hidden
	mkdir -p CustomizedElection/manifests

nginx:
	mkdir -p nginx_config/log
	cp templates/nginx_select.conf nginx_config/nginx_select.conf
	python configNginx.py

select:
	git clone -b dev https://sElectVoting:fc-dLEhqSKRG0exK@bitbucket.org/escapin/select.git sElect
	cd sElect; make devenv
	cp templates/config2js.js sElect/tools/config2js.js
	cp templates/refreshFilesVotingBooth.sh sElect/VotingBooth/refresh.sh
	cp sElect/templates/ElectionManifest.json _configFiles_/ElectionManifest.json


electionsClean:
	rm -rf elections/
	rm -rf elections_hidden/
	rm ElectionHandler/_data_/pwd.json
	cp templates/handlerConfigFile.json _configFiles_/handlerConfigFile.json


devclean: handlerclean nginxclean selectclean elclean


handlerclean:
	cd ElectionHandler; make clean
	-rm -rf _configFiles_
	-cd CustomizedElection; rm -rf node_modules

nginxclean:	
	-rm -rf nginx_config/

selectclean:
	-rm -rf sElect/

elclean:
	-rm -rf elections/
	-rm -rf elections_hidden/

