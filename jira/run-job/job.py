#!/usr/local/bin/python3

import os
import sys
import argparse
import json
import time
import random
import requests
import threading
import logging

import http.server

from urllib import parse

# import http.client as http_client

# http_client.HTTPConnection.debuglevel = 1
# logging.basicConfig()
# logging.getLogger().setLevel(logging.DEBUG)
# requests_log = logging.getLogger("requests.packages.urllib3")
# requests_log.setLevel(logging.DEBUG)
# requests_log.propagate = True

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Python script that waits until a JIRA Issue is in a given status')

    parser.add_argument("-u", "--jira-url",
                        default=os.environ.get('JIRA_URL', None))

    parser.add_argument("-t", "--jira-token",
                        default=os.environ.get('JIRA_TOKEN', None))

    parser.add_argument("-P", "--jira-api-path",
                        default=os.environ.get('JIRA_API_PATH', "/rest/api/2"))

    parser.add_argument("-I", "--issue-id",
                        default=os.environ.get('ISSUE_ID', None))

    parser.add_argument("-s", "--success-status",
                        default=os.environ.get('SUCCESS_STATUS', None))

    parser.add_argument("-S", "--success-status-code",
                        default=os.environ.get('SUCCESS_STATUS_CODE', None))

    parser.add_argument("-f", "--failed-status",
                        default=os.environ.get('FAILED_STATUS', None))

    parser.add_argument("-F", "--failed-status-code",
                        default=os.environ.get('FAILED_STATUS_CODE', None))


    parser.add_argument("-i", "--interval",
                        help="Polling period (seconds)",
                        type=int,
                        default=os.environ.get('INTERVAL', 60))

    parser.add_argument("-m", "--max-wait",
                        help="Max Wait (polling intervals)",
                        type=int,
                        default=os.environ.get('MAX_WAIT', 0))

    parser.add_argument("-v", "--verbose",
                        action="store_true")

    args = parser.parse_args()

    jira_token            = args.jira_token
    jira_url       = args.jira_url

    if not jira_token or not jira_url:
      print("Must provide JIRA URL and Token")
      sys.exit(1)
    
    jira_api_path  = args.jira_api_path

    issue_id       = args.issue_id.upper()

    if not issue_id:
      print("Must provide JIRA Issue ID")
      sys.exit(1)

    success_status = args.success_status.upper() if args.success_status else ""
    success_status_code = args.success_status_code

    failed_status = args.failed_status.upper() if args.failed_status else ""
    failed_status_code = args.failed_status_code
    
    # project_name     = args.project_name

    if not success_status and not success_status_code:
      print("Must provide success JIRA Status Name or Code")
      sys.exit(1)

    interval         = args.interval
    max_wait            = args.max_wait

    # branch = args.branch
    # gitlab_variables = args.gitlab_variables
    # job_name = args.job_name
    # artifact_name = args.artifact_name
    # artifact_is_json = args.artifact_is_json
    
    verbose = args.verbose

    base_url = jira_url + jira_api_path

    if verbose:
      print(base_url)

    headers = {
      'Authorization': 'Basic ' + jira_token
    }

    post_headers = {
      'authorization': 'Basic ' + jira_token,
      'content-type': 'application/json'
    }

    url = base_url + "/issue/" + issue_id

    if max_wait == 0:
      print(F"[{time.ctime()}] Checking status of {issue_id} [{url}] every {interval} seconds indefinitely.")
    else:
      print(F"[{time.ctime()}] Checking status of {issue_id} [{url}] every {interval} seconds for up to {max_wait} intervals.")
    
    c = 0
    while c <= max_wait:
      print(F"[{time.ctime()}] Checking status of {issue_id} [{url}]...")
      if verbose:
        print(F"GET on {url}")
      r = requests.get(url, headers=headers)

      if not r:
        print(F"[{time.ctime()}] Unable to check status of pipeline [GET {url}], status code {r.status_code}:")
        print(r.text)
        sys.exit(1)

      if verbose:
        print(r.json())

      status_name = r.json()['fields']['status']['name'].upper()
      status_code = r.json()['fields']['status']['id']
      
      print(F"[{time.ctime()}] Status is [{status_name}], status code [{status_code}]")
      if status_name == success_status or status_code == success_status_code:
        print(F"[{time.ctime()}] JIRA Issue {issue_id} is in state {status_name} (status ID ({status_code})) - SUCCESS!")
        print(F"SPINNAKER_PROPERTY_JIRA_STATUS={status_name}")
        print(F"SPINNAKER_PROPERTY_JIRA_STATUS_CODE={status_code}")
        print(F"SPINNAKER_PROPERTY_JIRA_COMPLETE=SUCCESS")
        sys.exit(0)

      if status_name == failed_status or status_code == failed_status_code:
        print(F"[{time.ctime()}] JIRA Issue {issue_id} is in state {status_name} (status ID ({status_code})) - FAILED!")
        print(F"SPINNAKER_PROPERTY_JIRA_STATUS={status_name}")
        print(F"SPINNAKER_PROPERTY_JIRA_STATUS_CODE={status_code}")
        print(F"SPINNAKER_PROPERTY_JIRA_COMPLETE=FAILURE")
        sys.exit(1)

      time.sleep(interval)

      if max_wait != 0:
        c += 1

    print(F"[{time.ctime()}] JIRA Issue {issue_id} didn't change to one of desired statuses within allotted time")
    print(F"[{time.ctime()}] JIRA Issue {issue_id} is in state {status_name} (status ID ({status_code})) - FAILED!")
    print(F"SPINNAKER_PROPERTY_JIRA_STATUS={status_name}")
    print(F"SPINNAKER_PROPERTY_JIRA_STATUS_CODE={status_code}")
    print(F"SPINNAKER_PROPERTY_JIRA_COMPLETE=INCOMPLETE")
    sys.exit(1)
