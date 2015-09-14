import os

src = os.stat("nginx_select.conf").st_mtime

while True:
    try:
      temp = os.stat("nginx_select.conf").st_mtime
      if src != temp:
        os.system("nginx -s reload")
        src = temp
        print("nginx reloaded")
    except: 
      pass