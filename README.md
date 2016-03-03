# ElectionManager
These files are used as a demonstration to show how to run nginx as a non-root user.

After a default nginx installation, the root directory is located at '/etc/nginx/', 
with the default configuration file '/etc/nginx/nginx.conf'. Either replace the default 
configuration file with the 'nginx.conf' file in this folder, or add the following lines
at the end of the 'http{' section:

    server {
        listen  80;
        server_name some.domain.org;
        location / {
            proxy_set_header    Host $host;
            proxy_set_header    X-Real-IP   $remote_addr;
            proxy_set_header    X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_pass  http://127.0.0.1:8080;
        }
    }

Inside 'nginx_nosu.conf' file in this folder replace all occurances of '/home/user/tmp/' with
a valid directory path (in which the user has read and write permissions).

Start nginx as root, this will bind port 80 and redirect to port 8080:
  $ sudo /usr/sbin/nginx 

Now you can start nginx with a new configuration file which doesn't use access restricted ports:
  $ /usr/sbin/nginx -c 'PATH/TO/nginx_nosu.conf'

To issure commands (such as reload and quit) to the secondary nginx processes, you also have to
specify the configuration file being used:
  $ /usr/sbin/nginx -c 'PATH/TO/nginx_nosu.conf' -s reload
  $ /usr/sbin/nginx -c 'PATH/TO/nginx_nosu.conf' -s quit
