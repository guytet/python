#!/usr/bin/env python

import urllib.request, json, logging

def get_email (email_mapping_url, github_uid):

    with urllib.request.urlopen(email_mapping_url) as url:
        data = json.loads(url.read().decode())

        for entry in data['users']:
           try:
               if (entry['github']).lower() == github_uid.lower():
                  return(entry['email'])

           except KeyError:
                  print('Key Error encoutred')
                  continue
           except AttributeError:
                  print('Attribute Error encoutred')
                  continue
           except TypeError:
                  print('Type Error encoutred')
                  continue

        try:
            match
        except NameError:
            str(github_uid)
            logging.info('Warning! could not find email match for github id ' + github_uid)
            pass
        else:
            pass
