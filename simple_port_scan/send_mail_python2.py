#!/usr/bin/python2
# Hardcoded to python2, kept for reference
# see python3 version in this dir

import smtplib
from email.mime.text import MIMEText
from email.MIMEMultipart import MIMEMultipart



def send_mail(host, port):

    fromaddr = 'port_scan@example.com'
    toaddr = 'user@example.com'

    msg = MIMEMultipart()

    msg['From'] = fromaddr
    msg['To'] = toaddr

    msg['Subject'] = "unallowed open port, action may be required"
    body = "check host %s port %s appears to be open" %(host, port)


    msg.attach(MIMEText(body, 'plain'))
    server = smtplib.SMTP('mail.example.com', 25)
    server.ehlo()
    server.starttls()
    text = msg.as_string()
    server.sendmail(fromaddr, toaddr, text)
