#!/usr/bin/env python

import socket, subprocess,re,sys,time
from datetime import datetime
from hosts_dict import my_dict
from send_mail import send_mail

"""  if not re.search(r'\b%d\b' %tested_port, str(allowed_ports) ):
\b represents 'word boundary', making the regex look for an exact match of the tested port """

for host_ip, allowed_ports in my_dict.items():

    for tested_port in range(1025):
  
        print tested_port
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.2)
        result = sock.connect_ex((host_ip, tested_port))


        if not result:

          if not re.search(r'\b%d\b' %tested_port, str(allowed_ports) ):
             send_mail(host_ip, tested_port)


        sock.close()
