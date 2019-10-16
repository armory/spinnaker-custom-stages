#!/usr/local/bin/python3

import os
import sys
import argparse
import json
import time
import random
import requests
import threading

import http.server

from urllib import parse


# import socketserver


if __name__ == '__main__':
    # print("Starting demo datadog app.")
    parser = argparse.ArgumentParser(description='Python script that checks the status of Datadog monitors for some time period')

    parser.add_argument("-i", "--interval",
                        help="Polling period (seconds)",
                        type=int,
                        default=os.environ.get('INTERVAL', 60))

    parser.add_argument("-c", "--count",
                        help="Count",
                        type=int,
                        default=os.environ.get('COUNT', 10))

    parser.add_argument("-m", "--monitor-id",
                        default=os.environ.get('DD_MONITOR_ID', None))

    parser.add_argument("-k", "--datadog-api-key",
                        default=os.environ.get('DD_API_KEY', None))

    parser.add_argument("-K", "--datadog-app-key",
                        default=os.environ.get('DD_APP_KEY', None))

    parser.add_argument("-S", "--allowed-statuses",
                        default=os.environ.get('ALLOWED_STATUSES', "OK"))

    parser.add_argument("-e", "--datadog-endpoint",
                        default=os.environ.get('DATADOG_ENDPOINT', "https://api.datadoghq.com"))

    parser.add_argument("-p", "--datadog-path",
                        default=os.environ.get('DATADOG_ENDPOINT', "/api/v1/monitor"))

    ## TODO take environment variable for this
    parser.add_argument("-v", "--verbose",
                        action="store_true")

    # parser.add_argument("-a", "--app-name",
    #                     help="App name",
    #                     default=os.environ.get('DD_APP_NAME', 'default'))

    args = parser.parse_args()

    monitor_id       = args.monitor_id
    datadog_api_key  = args.datadog_api_key
    datadog_app_key  = args.datadog_app_key

    if not monitor_id or not datadog_api_key or not datadog_app_key:
      print("Must provide Datadog API Key, Datadog App Key, and Monitor ID")
      sys.exit(1)

    interval         = args.interval
    count            = args.count
    datadog_endpoint = args.datadog_endpoint
    datadog_path     = args.datadog_path
    verbose          = args.verbose
    allowed_statuses         = args.allowed_statuses.split(',')


    url = datadog_endpoint + datadog_path + '/' + monitor_id

    params = {
      'group_states': 'all',
      'api_key': datadog_api_key,
      'application_key': datadog_app_key
    }

    if verbose:
      print(url)

    c = 0
    unhealthy_groups = []

    # We start at time 0, and poll count + 1 times, to cover a time range of (interval * count)
    while c <= count:

      r = requests.get(url, params=params)
      print(F"[{time.ctime()}] Checking monitor ID {monitor_id}...")
      body = r.json()
      groups = body['state']['groups']
      if verbose:
        print(body['state']['groups'])
      
      for group in groups.values():
        if group['status'] not in allowed_statuses:
          unhealthy_groups.append(group)

      if len(unhealthy_groups) > 0:
        break
      print("No unhealthy groups")

      time.sleep(interval)

      c += 1

    output = {
      "unhealthy_count": len(unhealthy_groups),
      "unhealthy_groups": unhealthy_groups,
      "successful_polls": c,
      "status": "SUCCESSFUL" if len(unhealthy_groups) == 0 else "FAILED",
      "success": len(unhealthy_groups) == 0
    }
    print(F"SPINNAKER_CONFIG_JSON={json.dumps(output)}")
    if len(unhealthy_groups) > 0:
      sys.exit(1)
