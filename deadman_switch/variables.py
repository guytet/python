# which ssh user should be parsed for in /var/log/auth.log
SSH_USER = ''

# Fine to leave as is
SMTP_SERVER = 'smtp.mail.yahoo.com'
SMTP_PORT = 465

# Your yhaoo address
SENDER_ADDRESS = ''
SENDER_NAME = ''

# Yahoo requires app passowrd to be created when SAML isn't used for access
YAHOO_APP_PASSWORD = ''

# List for recipients
RECIPIENTS = []

BIN_DIR="/usr/local/bin/deadman_switch"
CRITICAL_MESSAGE_FILE="/usr/local/bin/deadman_switch/critical_message.txt"
WARNING_MESSAGE_FILE="/usr/local/bin/deadman_switch/warning_message.txt"
