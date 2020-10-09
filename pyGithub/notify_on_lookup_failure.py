#!/usr/bin/env python

import requests,os,logging

token=(os.environ['PR_BOT_SLACK_OAUTH_TOKEN'])
slack_channels=['AAAAAAAA', 'BBBBBBBB']  

no_notify_users=['some_user_a', 'some_user_b']


def notify_failure(reviewer, url):
   text_a='Email lookup has failed for github UID: '
   text_b=' who was asked to review PR: '

   for channel in slack_channels:

       if reviewer in no_notify_users:
           logging.info(reviewer + ' is excluded from failure notifications - not sending slack messages')
           break

       data = {
       'token': token,
       'channel': channel,
       'as_user': 'true',
       'text': (text_a + reviewer + text_b + url)
       }

       logging.info('sending slack message to notify failure for lookup '  + ' for PR ' + url)
       requests.post('https://slack.com/api/chat.postMessage', data=data)
