# local file in this dir
import variables

import sys
import json
import smtplib
import inspect
import argparse
from pathlib import Path
from datetime import datetime, timedelta
from email.message import EmailMessage
from email.utils import formataddr

class YahooMailer:
    def __init__(self, args, log_func, state_file, state, alert_severity):
        self.args            = args
        self.log             = log_func
        self.state_file      = state_file
        self.state           = state
        self.in_testing      = self.args.testing
        self.alert_severity  = alert_severity

        self.msg             = EmailMessage()
        self.msg['Subject']  = self.set_message_subject()
        self.msg['From']     = formataddr((variables.SENDER_NAME, variables.SENDER_ADDRESS))
        self.msg['To']       = ', '.join(variables.RECIPIENTS)

        self.state["num_warnings"] = self.state.get("num_warnings", 0)
        self.state["num_critical"] = self.state.get("num_critical", 0)

        self.log(f"num_warnings: {self.state['num_warnings']}") ###
        self.log(f"num_critical: {self.state['num_critical']}") ###

        self.assemble_paths()

    def set_message_subject(self):
        if self.alert_severity == "warning":
            subject = f"Automated warning message for {variables.SENDER_NAME.split()[0]}"
            return subject

        if self.alert_severity == "critical":
            subject = f"Automated message from {variables.SENDER_NAME.split()[0]}"
            return subject

    def assemble_paths(self):
        self.warning_file_path=Path(
            variables.BIN_DIR).joinpath(variables.WARNING_MESSAGE_FILE
        )
        self.critical_file_path=Path(
            variables.BIN_DIR).joinpath(variables.CRITICAL_MESSAGE_FILE
        )


    def run(self):
        self.log(f"received severity {self.alert_severity}")

        message_file = self.set_message_file()

        if message_file:
            if self.check_alert_log():
                self.log(f"will send {self.alert_severity} message")
                self.send_email(message_file)
                self.increase_alert_counters()


    def check_alert_log(self):
        if self.alert_severity == "warning":
            if self.state['num_warnings'] <= 1 and self.state['num_critical'] == 0:
                return True
        if self.alert_severity == "critical":
            if self.state['num_warnings'] > 1 and self.state['num_critical'] <= 1:
                return True
        return None


    def increase_alert_counters(self):
        if self.alert_severity == "warning":
            self.state['num_warnings'] += 1
            self.state_file.write_text(json.dumps(self.state))

        if self.alert_severity == "critical":
            self.state['num_critical'] += 1
            self.state_file.write_text(json.dumps(self.state))


    def set_message_file(self):
        if self.alert_severity == "warning":
            self.log(f"returning {self.warning_file_path}")
            return self.warning_file_path

        if self.alert_severity == "critical":
            self.log(f"returning {self.critical_file_path}")
            return self.critical_file_path

        self.log(f"returning {self.alert_severity}")
        return None


    def write_alert_log(self, message_file):
        pass

    def send_email(self, message_file):
        # strip() is required so the email body won't be treated as quoted text
        with open(message_file, 'r', encoding='utf-8') as file:
            self.msg.set_content(file.read().strip())

        # Send the email
        with smtplib.SMTP_SSL(variables.SMTP_SERVER, variables.SMTP_PORT, timeout=30) as smtp:
            smtp.set_debuglevel(1)
            smtp.login(variables.SENDER_ADDRESS, variables.YAHOO_APP_PASSWORD)
            smtp.send_message(
                self.msg,
                from_addr=variables.SENDER_ADDRESS, 
                to_addrs=variables.RECIPIENTS
            )

        self.log("Email sent successfully!")
        return True

