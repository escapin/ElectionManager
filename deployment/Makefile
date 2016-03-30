default:
	@echo Specify the goal: depenv OR depclean

depenv: nginxFiles updateNginxConfig

nginxFiles:
	cp -n template/serverAddresses.json .
	cp -n template/nginx_root.conf .
	mkdir -p nginx_config/log

updateNginxConfig:
	python configNginx.py

depclean: 
	-rm -rf nginx_config
	-rm serverAddresses.json
	-rm nginx_root.conf
