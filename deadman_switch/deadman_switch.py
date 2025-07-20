# local file in this dir
import variables
# local class for using Yahoo as SMTP
from yahoo_mailer import YahooMailer

import sys
import json
import smtplib
import inspect
import argparse
from pathlib import Path
from datetime import datetime, timedelta
from email.message import EmailMessage
from email.utils import formataddr

class LogFileParser:
    def __init__(self, args, log_func, auth_log_file, state_file):
        self.args            = args
        self.log             = log_func

        self.auth_log_file   = auth_log_file
        self.state_file      = Path(state_file)
        self.state           = self.open_state_file(state_file)

        self.threshold       = self.args.threshold
        self.in_testing      = self.args.testing

        self.delta           = timedelta(seconds=self.threshold)

        self.severity        = "normal"

    def open_state_file(self, state_file):
        state_file = Path(state_file)
        if state_file.exists():
            state = json.loads(state_file.read_text())
            return state
        else:
            return {}

    def open_file(self):
        with open(self.auth_log_file, 'r') as file:
            return self.parse_file(file)

    def parse_file(self, file):
        most_recent_matched_line = None
        for line in file:
            if f"Accepted publickey for {variables.SSH_USER}" in line:
                most_recent_matched_line = line
        return most_recent_matched_line

    def assemble_date_object(self, matched_line):
        timestamp_str = matched_line[:15]
        current_year = datetime.now().year
        return datetime.strptime(f"{current_year} {timestamp_str}", "%Y %b %d %H:%M:%S")

    def compare_date(self, last_login_timestamp):
        now = datetime.now().replace(microsecond=0)
        threshold = now - self.delta
        if last_login_timestamp > threshold:
            return True
        else:
            self.log(f"{threshold} is older than {last_login_timestamp} checking which severity should be set")
            return False

    def update_state_file(self, last_login_timestamp):
        time_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.state["last_run"] = time_now
        self.state["last_login"] = last_login_timestamp.isoformat()
        self.state_file.write_text(json.dumps(self.state))

    def determine_time_since_last_login(self, last_login_timestamp):
        delta = datetime.now() - last_login_timestamp
        seconds_since_last_login = int(delta.total_seconds())
        self.log(f"last login was {seconds_since_last_login} seconds ago")
        return self.set_severity(seconds_since_last_login)

    def set_severity(self, seconds_since_last_login):
        if seconds_since_last_login > self.threshold * 4:
            return "critical"
        if seconds_since_last_login > self.threshold * 3:
            return "warning"
        return "normal"

    def run(self):
        matched_line = self.open_file()
        if matched_line:
            last_login_timestamp = self.assemble_date_object(matched_line)
            is_recent = self.compare_date(last_login_timestamp)

            if is_recent:
                self.update_state_file(last_login_timestamp)
                self.severity = "normal"
            else:
                self.severity = self.determine_time_since_last_login(last_login_timestamp)
        else:
            self.log("No matching login found in log file.")
            self.severity = "normal"

        return self.severity, self.state_file, self.state


def parse_args():
    parser = argparse.ArgumentParser(
        description="Check for last login of a given user according to /var/log/auth.log."
    )

    parser.add_argument(
        "--threshold", required=True, type=int,
        help=(
            "Number of seconds since last login to consider as threshold. "
            "multiplied by 3 triggers warning alerts, by 4 triggers critical alerts"
        )
    )

    parser.add_argument(
        "--testing", action="store_true",
        help=(
            "enables different workflows when provided, optional (currently not in use)"
        )
    )

    args = parser.parse_args()
    return args


def log_func(msg):
    stack = inspect.stack()
    current = stack[1].function
    print(f"[{current}] {msg}")


def main():
    args = parse_args()
    parser = LogFileParser(
                 args,
                 log_func,
                 '/var/log/auth.log',
                 '/var/log/deadman_switch/deadman_check.json'
             )
    alert_severity, state_file, state = parser.run()

    sender =  YahooMailer(args, log_func, state_file, state, alert_severity)
    sender.run()

if __name__ == "__main__":
    main()

