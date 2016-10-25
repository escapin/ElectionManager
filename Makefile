default:
	@echo Specify the goal: devenv OR devclean

devenv: handler custom nginx select


handler:
	cd ElectionHandler; make
	mkdir -p _configFiles_
	cp templates/config.json _configFiles_/handlerConfigFile.json
	mkdir -p elections

custom:
	cd CustomizedElection; make
	mkdir -p elections_hidden

nginx:
	mkdir -p nginx_config/log
	cp templates/nginx_select.conf nginx_config/nginx_select.conf
	python configNginx.py

select:
	git clone -b dev https://sElectVoting:fc-dLEhqSKRG0exK@bitbucket.org/escapin/select.git sElect
	cd sElect; make devenv
	cp templates/refreshFilesVotingBooth.sh sElect/VotingBooth/refresh.sh
	cp sElect/templates/ElectionManifest.json _configFiles_/ElectionManifest.json

electionsClean:
	rm -rf elections/
	rm -rf elections_hidden/
	rm ElectionHandler/_data_/pwd.json
	cp templates/handlerConfigFile.json _configFiles_/handlerConfigFile.json


devclean: handlerclean customclean nginxclean selectclean elclean


handlerclean:
	cd ElectionHandler; make clean
	-rm -rf _configFiles_

customclean:
	cd CustomizedElection; make clean

nginxclean:	
	-rm -rf nginx_config/

selectclean:
	-rm -rf sElect/

elclean:
	-rm -rf elections/
	-rm -rf elections_hidden/

