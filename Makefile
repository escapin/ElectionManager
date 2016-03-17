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
	cp templates/ElectionConfigFile.json ./ElectionConfigFile.json
	mkdir -p elections

select:
	git clone https://github.com/escapin/sElect.git
	cd sElect; make devenv
	cp templates/config2js.js sElect/tools/config2js.js
	cp templates/refreshConfig.sh sElect/VotingBooth/refreshConfig.sh


devclean: configclean selectclean elclean

configclean:
	cd ElectionHandler; make clean
	-rm ElectionConfigFile.json
	-rm -rf nginx_config/

selectclean:
	-rm -rf sElect/
elclean:
	-rm -rf elections/


restart:
	-rm nginx_config/handler/nginx_select.conf
	-rm ElectionConfigFile.json
	cp templates/nginx_select.conf nginx_config/handler/nginx_select.conf
	cp templates/ElectionConfigFile.json ./ElectionConfigFile.json
	python configNginx.py
