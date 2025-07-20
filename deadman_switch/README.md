# Deadman Switch – SSH Login Monitor & Email Notifier

`deadman_switch` is a Python utility that monitors a Linux system's SSH login activity and sends email alerts if a specific user has not logged in within a configured time threshold. It uses log parsing and configurable thresholds to determine whether a "warning" or "critical" email should be triggered.

---

## Use Case

Ideal for environments where regular logins are expected from a specific account, and their absence may indicate an issue - such as compromised access, automation failure, or system outage.

---

## Features

- Parses `/var/log/auth.log` for the last `Accepted publickey for <user>` entry
- Determines alert level based on elapsed time since last login
- Sends warning or critical emails via Yahoo SMTP
- Maintains state (last login, previous alerts) in a JSON file
- Supports configurable threshold values
- Designed to run from cron or systemd timer

---

## Setup

### 1. Prerequisites

- Python 3.6+
- Yahoo account with [App Passwords enabled](https://help.yahoo.com/kb/SLN15241.html)
- Access to `/var/log/auth.log` (typically requires root)

### 2. Configuration

Edit the `variables.py` file with your environment details:

```python
SSH_USER = 'your_ssh_user'
SENDER_ADDRESS = 'your_yahoo_email@example.com'
SENDER_NAME = 'Your Name'
YAHOO_APP_PASSWORD = 'your_app_password'
RECIPIENTS = ['recipient1@example.com', 'recipient2@example.com']

