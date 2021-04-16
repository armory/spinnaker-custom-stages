# JIRA Webhook Stages

Spinnaker allows you to define custom webhooks which show up in the Spinnaker UI.

For halyard based configuration. each custom stage can be configured by creating an entry in `/home/spinnaker/.hal/default/profiles/orca-local.yml` (create this file if it does not exist)

For operator based configuration, add to:

```yml
apiVersion: spinnaker.armory.io/v1alpha2
kind: SpinnakerService
metadata:
  name: spinnaker
spec:
  spinnakerConfig:
    profiles:
      orca:
        webhook:
          preconfigured:
```

The basic format of this portion of the file looks like this:

The basic layout of each stage looks like this:

```yml
webhook:
  preconfigured:
  - label: "Stage A"
    # more properties for stage A...
  - label: "Stage B"
    # more properties for stage B...
```

Here is an example of a stage:

```yml
...
  - # stage name in stage selector drop down
    label: "Stage A"
    enabled: true
    # UI description for stage
    description: Custom stage
    # stage 'type' in stage definition
    type: addJiraIss
    # Webhook type
    method: POST
    # URL for webhook call
    url: http://something.domain.com:8080/api/v2/dosomething
    customHeaders:
      # Any necessary headers (supports S3 / Vault)
      Authorization: Basic c2VydmljZWFjY291bnQ6cGFzc3dvcmQK
      Content-Type: application/json
    # Payload for the request
    payload: |-
      {
        "key": "${parameterValues['item']}"
      }
    # Zero or more parameters
    parameters:
    - label: Item
      name: item
      description: Text description
      type: string
```

Authorization:

*Update the authorization with the base64 encoded version of `username:password`*

For example, if your JIRA service account username is `username` and your password is `password`, then do this:

```bash
$ echo -n 'serviceaccount:password' | base64
c2VydmljZWFjY291bnQ6cGFzc3dvcmQ=
```

And then your auth header will look like this (this is a "Basic Auth" header)

```yml
      Authorization: Basic c2VydmljZWFjY291bnQ6cGFzc3dvcmQ=
```

Capitalization of `Basic` matters.  So does the `-n` in the echo (which removes the trailing endline).

## JIRA Stages

Here is an example set of stage definitions that do the following:

* Create JIRA Issue (with given project, description, summary, and type)
* Comment on a given JIRA Issue
* Update a given JIRA Issue (update description and summary)
* Transition the JIRA Issue to a new status

You can mix and match and modify these (for example, rather than a generic 'JIRA: Transition Issue' stage, you could have a "JIRA: Transition to Done" with a hardcoded target stage ID of 41)

```yml
webhook:
  preconfigured:
  - label: "JIRA: Create Issue"
    type: addJiraIss
    enabled: true
    description: Custom stage that add an Issue in Jira
    method: POST
    url: http://jira.domain.com:8080/rest/api/2/issue
    customHeaders:
      Authorization: Basic c2VydmljZWFjY291bnQ6cGFzc3dvcmQK
      Content-Type: application/json
    payload: |-
      {
        "fields": {
            "project":
            {
              "key": "${parameterValues['projectid']}"
            },
            "summary": "${parameterValues['summary']}",
            "description": "${parameterValues['description']}",
            "issuetype": {
              "name": "${parameterValues['issuetype']}"
            },
            "priority": {
              "name": "${parameterValues['priority']}"
            }
        }
      }
    parameters:
    - label: Project ID ("ENG" or "DOCS")
      name: projectid
      description: Which JIRA project do you want to create an item in?
      type: string
    - label: Issue Type ("Improvement", "Task", "New Feature", or "Bug")
      name: issuetype
      description: issuetype
      type: string
    - label: Priority ("Low", "Medium", or "High")
      name: priority
      description: priority
      type: string
    - label: Issue Summary
      name: summary
      description: summary
      type: string
    - label: Description
      name: description
      description: description
      type: string
  - label: "JIRA: Comment on Issue"
    type: comJiraIss
    enabled: true
    description: Custom stage that posts a comment in a Jira Issue
    method: POST
    url: http://jira.domain.com:8080/rest/api/2/issue/${parameterValues['issue']}/comment
    customHeaders:
      Authorization: Basic c2VydmljZWFjY291bnQ6cGFzc3dvcmQK
      Content-Type: application/json
    payload: |-
      {
        "body": "${parameterValues['message']}"
      }
    parameters:
    - label: Issue ID
      name: issue
      description: Issue
      type: string
    - label: Message
      name: message
      description: message
      type: string
  - label: "JIRA: Update Issue"
    type: updJiraIss
    enabled: true
    description: Custom stage that updates an Issue in Jira
    method: PUT
    url: http://jira.domain.com:8080/rest/api/2/issue/${parameterValues['issue']}
    customHeaders:
      Authorization: Basic c2VydmljZWFjY291bnQ6cGFzc3dvcmQK
      Content-Type: application/json
    payload: |-
      {
        "update": {
            "summary": [
                {
                    "set": "${parameterValues['summary']}"
                }
            ],
            "description": [
                {
                    "set": "${parameterValues['description']}"
                }
            ]
        }
      }
    parameters:
    - label: Issue ID
      name: issue
      description: Issue
      type: string
    - label: Summary
      name: summary
      description: summary
      type: string
    - label: Description
      name: description
      description: description
  - label: "JIRA: Transition Issue"
    type: transJiraIss
    enabled: true
    description: Custom stage that transitions an Issue in Jira
    method: POST
    url: http://jira.domain.com:8080/rest/api/2/issue/${parameterValues['issue']}/transitions
    customHeaders:
      Authorization: Basic c2VydmljZWFjY291bnQ6cGFzc3dvcmQK
      Content-Type: application/json
    payload: |-
      {
        "transition": {
          "id": "${parameterValues['targetStageID']}"
        }
      }
    parameters:
    - label: Issue ID
      name: issue
      description: Issue
      type: string
    - label: Target Stage ID
      name: targetStageID
      description: Target Stage ID (11 is "To Do", 21 is "In Progress", 31 is "In Review", 41 is "Done")
      type: string
```
