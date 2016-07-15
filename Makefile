default:
	@echo Specify the goal: devenv OR devclean

devenv: handler nginx select


handler:
	cd ElectionHandler; make
	mkdir -p _handlerConfigFiles_
	cp templates/handlerConfigFile.json _handlerConfigFiles_/handlerConfigFile.json
	mkdir -p elections
	mkdir -p elections_hidden

nginx:
	mkdir -p nginx_config/log
	cp templates/nginx_select.conf nginx_config/nginx_select.conf
	python configNginx.py

select:
	git clone -b master https://github.com/escapin/sElect.git
	cd sElect; make devenv
	cp templates/config2js.js sElect/tools/config2js.js
	cp templates/refreshFilesVotingBooth.sh sElect/VotingBooth/refresh.sh
	cp sElect/templates/ElectionManifest.json _handlerConfigFiles_/ElectionManifest.json


electionsClean:
	rm -rf elections/
	rm -rf elections_hidden/
	rm ElectionHandler/_data_/pwd.json
	cp templates/handlerConfigFile.json _handlerConfigFiles_/handlerConfigFile.json


devclean: handlerclean nginxclean selectclean elclean


handlerclean:
	cd ElectionHandler; make clean
	-rm -rf _handlerConfigFiles_

nginxclean:	
	-rm -rf nginx_config/

selectclean:
	-rm -rf sElect/

elclean:
	-rm -rf elections/
	-rm -rf elections_hidden/

