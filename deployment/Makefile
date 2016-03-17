default:
	@echo Specify the goal: devenv OR devclean

devenv: nginx

nginx:
	mkdir -p nginx_config/log
	cp ./nginx_root.conf nginx_config/nginx_root.conf
	python configNginx.py