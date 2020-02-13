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



# import socketserver


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Python script that runs a GitLab Pipeline and monitors / checks its health status')

    parser.add_argument("-t", "--gitlab-token",
                        default=os.environ.get('GITLAB_TOKEN', None))

    parser.add_argument("-u", "--gitlab-url",
                        default=os.environ.get('GITLAB_URL', None))

    parser.add_argument("-P", "--gitlab-api-path",
                        default=os.environ.get('GITLAB_API_PATH', "/api/v4"))

    parser.add_argument("-p", "--project-id",
                        default=os.environ.get('PROJECT_ID', None))

    parser.add_argument("-n", "--project-name",
                        default=os.environ.get('PROJECT_NAME', None))

    parser.add_argument("-i", "--interval",
                        help="Polling period (seconds)",
                        type=int,
                        default=os.environ.get('INTERVAL', 60))

    parser.add_argument("-m", "--max-wait",
                        help="Max Wait (polling intervals)",
                        type=int,
                        default=os.environ.get('MAX_WAIT', 0))

    parser.add_argument("-b", "--branch",
                        default=os.environ.get('BRANCH', "master"))

    # TODO support variables
    parser.add_argument("-e", "--gitlab_variables",
                        help="Variables to pass to the GitLab Pipeline (format: 'hello=world|key=variable|FILE:filename=input.file)",
                        default=os.environ.get('GITLAB_VARIABLES', None))

    parser.add_argument("-j", "--job-name",
                        default=os.environ.get('JOB_NAME', None))

    parser.add_argument("-a", "--artifact-name",
                        default=os.environ.get('ARTIFACT_NAME', None))

    parser.add_argument("-J", "--artifact-is-json",
                        action="store_true")

    ## TODO take environment variable for this
    parser.add_argument("-v", "--verbose",
                        action="store_true")

    args = parser.parse_args()

    gitlab_token            = args.gitlab_token
    gitlab_url       = args.gitlab_url

    if not gitlab_token or not gitlab_url:
      print("Must provide GitLab URL and Token")
      sys.exit(1)
    
    gitlab_api_path  = args.gitlab_api_path

    project_id       = args.project_id
    project_name     = args.project_name

    if not project_id and not project_name:
      print("Must provide GitLab Project ID or Namespaced Project Name (for example, 'superteam/my-awesome-project')")
      sys.exit(1)

    interval         = args.interval
    max_wait            = args.max_wait
    branch = args.branch
    gitlab_variables = args.gitlab_variables
    job_name = args.job_name
    artifact_name = args.artifact_name
    artifact_is_json = args.artifact_is_json
    
    verbose = args.verbose

    base_url = gitlab_url + gitlab_api_path

    if verbose:
      print(base_url)

    headers = {
      'Authorization': 'Bearer ' + gitlab_token
    }

    post_headers = {
      'authorization': 'Bearer ' + gitlab_token,
      'content-type': 'application/json'
    }

    # If you have variable names that start with `FILE:`, they get treated as files.
    # If you want an env variable name that starts with `FILE:`, that just won't work right now.  Sorry.
    variables = []
    if gitlab_variables:
      for gitlab_variable in gitlab_variables.split('|'):
        i = gitlab_variable.find('=')
        # print(i)
        if gitlab_variable.startswith('FILE:'):
           # Need at least one character, otherwise ignored
          if i > 5:
            variables.append({'key': gitlab_variable[5:i],
                              'value': gitlab_variable[i+1:],
                              'variable_type': 'file'})
        else:
          if i > 0:
            variables.append({'key': gitlab_variable[0:i],
                              'value': gitlab_variable[i+1:],
                              'variable_type': 'env_var'})

    # print(variables)
    # sys.exit(0)
    json_body = {'ref': branch, 'variables': variables}

    # If we don't have a project ID, use project name to get project ID (if we have both, project ID takes precedence)
    if project_id:
      try:
        project_id = int(project_id)
      except:
        print(F"Invalid project ID '{project_id}', must be integer")
        sys.exit(1)
      print(F"[{time.ctime()}] Using project ID {project_id}...")
    else:
      print(F"[{time.ctime()}] Using project name {project_name} to get project ID...")
      url = base_url + '/projects'
      if verbose:
        print(F"GET on {url}")
      r = requests.get(url, headers=headers)

      if not r:
        print(F"[{time.ctime()}] Unable to get project ID [GET {url}], status code {r.status_code}:")
        print(r.text)
        sys.exit(1)

      body = r.json()
      if verbose:
        print(body)

      l = list(filter(lambda x: x['path_with_namespace'] == project_name, body))
      if len(l) == 0:
        print(F"[{time.ctime()}] Couldn't find project named {project_name}...")
        sys.exit(1)

      project_id = int(l[0]['id'])
      print(F"[{time.ctime()}] Identified project ID {project_id}")


    print(F"[{time.ctime()}] Triggering a build in project ID {project_id}, on branch [{branch}], with variables {variables}")
    url = base_url + '/projects/' + str(project_id) + '/pipeline'
    if verbose:
      print(F"POST on {url}")
      print(json_body)
    r = requests.post(url, headers=post_headers, json=json_body)

    if not r:
      print(F"[{time.ctime()}] Unable to trigger pipeline [POST {url}], body [{json.dumps(json_body)}], status code {r.status_code}:")
      print(r.text)
      if r.status_code == 400:
        print(f"Try checking the pipeline definition for branch {branch}")
      sys.exit(1)
  
    body = r.json()
    if verbose:
      print(body)

    pipeline_id = body['id']
    web_url = body['web_url']
    print(F"[{time.ctime()}] Triggered pipeline #{pipeline_id} in project ID {project_id}.  URL for build is {web_url}")
    print(F"SPINNAKER_PROPERTY_BUILD_URL={web_url}")
    if max_wait == 0:
      print(F"[{time.ctime()}] Checking status every {interval} seconds indefinitely.")
    else:
      print(F"[{time.ctime()}] Checking status every {interval} seconds for up to {max_wait} intervals.")
    
    c = 0
    while c <= max_wait:
      print(F"[{time.ctime()}] Checking status of project ID {project_id} pipeline #{pipeline_id}...")
      url = base_url + '/projects/' + str(project_id) + '/pipelines/' + str(pipeline_id)
      if verbose:
        print(F"GET on {url}")
      r = requests.get(url, headers=headers)

      if not r:
        print(F"[{time.ctime()}] Unable to check status of pipeline [GET {url}], status code {r.status_code}:")
        print(r.text)
        sys.exit(1)

      if verbose:
        print(r.json())

      status = r.json()['status']
      print(F"[{time.ctime()}] Status is [{status}]")
      if status == 'success' or status == 'failed':
        break

      time.sleep(interval)

      if max_wait != 0:
        c += 1
    print(F"SPINNAKER_PROPERTY_BUILD_STATUS={status}")


    # If pipeline has failed or is still running (or pending), print status and exit
    if status == 'pending' or status == 'running':
      print(F"[{time.ctime()}] Project ID {project_id} pipeline #{pipeline_id} didn't complete in the allotted time (status is '{status}')")
      sys.exit(1)
    elif status == 'failed':
      print(F"[{time.ctime()}] Project ID {project_id} pipeline #{pipeline_id} build FAILED (status is '{status}')")
      sys.exit(1)

    print(F"[{time.ctime()}] Project ID {project_id} pipeline #{pipeline_id} build COMPLETED (status is '{status}')")

    if job_name and artifact_name and len(job_name) > 0 and len(artifact_name) > 0:
      print(F"[{time.ctime()}] Identifying job '{job_name}' from project ID {project_id} pipeline #{pipeline_id}")
      url = base_url + '/projects/' + str(project_id) + '/pipelines/' + str(pipeline_id) + '/jobs'
      if verbose:
        print(F"GET on {url}")
      r = requests.get(url, headers=headers)

      if not r:
        print(F"[{time.ctime()}] Unable to get job list for pipeline [GET {url}], status code {r.status_code}:")
        print(r.text)
        sys.exit(1)

      body = r.json()
      j = list(filter(lambda x: x['name'] == job_name, body))

      if len(j) == 0:
        print(F"[{time.ctime()}] Job called '{job_name}' not found for pipeline.")
        print(r.text)
        sys.exit(1)

      job_id = j[0]['id']
      print(F"[{time.ctime()}] Identified job '{job_id}' from project ID {project_id} pipeline #{pipeline_id}")

      url = base_url + '/projects/' + str(project_id) + '/jobs/' + str(job_id) + '/artifacts/' + artifact_name
      if verbose:
        print(F"GET on {url}")
      r = requests.get(url, headers=headers)

      if not r:
        print(F"[{time.ctime()}] Unable to get artifact for pipeline [GET {url}], status code {r.status_code}:")
        print(r.text)
        sys.exit(1)

      content_type = r.headers.get('content-type')
      if verbose:
        print(r.content)

      if artifact_is_json or content_type.split(';')[0] == 'application/json':
        body = r.json()
        print(F"SPINNAKER_CONFIG_JSON={json.dumps(body)}")

      else:
        content = r.content
        for line in content.splitlines():
          print(F"SPINNAKER_PROPERTY_{line.decode('utf-8')}")
    else:
      print(F"[{time.ctime()}] Job and artifact not populated, not retrieving metadata")