import os
from time import sleep

src = os.stat("nginx_select.conf").st_mtime

while True:
    sleep(0.1)
    try:
      temp = os.stat("nginx_select.conf").st_mtime
      if src != temp:
        os.system("nginx -s reload")
        src = temp
        print("nginx reloaded")
    except: 
      pass
