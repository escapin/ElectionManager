default:
	@echo Specify the goal: depenv OR depclean

depenv: nginxFiles updateConfig 

nginxFiles:
	cp -n templates/nginx_root.conf .
	mkdir -p nginx_config/log

updateConfig:
	python configNginx.py
	python configDeployment.py

depclean: 
	-rm -rf nginx_config
	-rm nginx_root.conf
