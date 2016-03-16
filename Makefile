default:
	@echo Specify the goal: devenv OR devclean

devenv: nginx handler select

nginx:
	mkdir -p nginx_config/handler/log
	mkdir -p nginx_config/root/log
	cp templates/nginx_root.conf nginx_config/root/nginx_root.conf
	cp templates/nginx_select.conf nginx_config/handler/nginx_select.conf
	python configNginx.py

handler:
	cd ElectionHandler; make
	mkdir _handlerConfigFiles_
	cp templates/handlerConfigFile.json _handlerConfigFiles/handlerConfigFile.json
	cp templates/serverAddresses.json _handlerConfigFiles/serverAddresses.json
	mkdir -p elections

select:
	git clone -b merging https://github.com/escapin/sElect.git
	cd sElect; make devenv
	cp templates/config2js.js sElect/tools/config2js.js
	cp templates/refreshFilesVotingBooth.sh sElect/VotingBooth/refresh.sh



devclean: handlerclean configclean selectclean elclean


handlerclean:
	cd ElectionHandler; make clean

configclean:
	-rm -rf _handlerConfigFiles_
	-rm -rf nginx_config/

selectclean:
	-rm -rf sElect/
	
elclean:
	-rm -rf elections/


	
