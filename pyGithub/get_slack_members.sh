#!/usr/bin/env bash

slack_members_file="/tmp/slackMembers.json"

if [ -f "$slack_members_file" ]; then

    if [[ $(find "$slack_members_file" -mtime +1 -print) ]]; then
        echo "slack members file exits, but older than one day, getting a new copy"
        curl -s "https://slack.com/api/users.list?token=$SLACKBOT_API_TOKEN" | jq '.' > "$slack_members_file"
    fi

else
       echo "slack members file does not exist, getting it..."
       curl -s "https://slack.com/api/users.list?token=$SLACKBOT_API_TOKEN" | jq '.' > "$slack_members_file"
fi
