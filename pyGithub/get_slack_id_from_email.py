#!/usr/bin/env python

import json,subprocess

def get_slack_id (email_address):
    
    # curls a new copy of Slack members, only current copy is older than 1 day
    subprocess.call('/github_app/github_app/get_slack_members.sh')

    with open('/tmp/slackMembers.json') as json_file:
      data = json.load(json_file)

      for entry in data['members']:
         try:
            if (entry['profile']['email']).lower() == email_address.lower():
              return (entry['id'])
         except KeyError:
              continue
         except AttributeError:
              continue
