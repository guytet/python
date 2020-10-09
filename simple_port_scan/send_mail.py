#!/usr/bin/python3

import smtplib

sender = 'result@example.com'
receivers = ['user@example.com']

message = """From: result_message <result@example.com>
To: <admin@example.com>
Subject: SMTP e-mail test

This is a test e-mail message.
"""

try:
   smtpObj = smtplib.SMTP('mail.example.com', 25)
   smtpObj.sendmail(sender, receivers, message)         
   print("Successfully sent email")
except SMTPException:
   print("Error: unable to send email")
