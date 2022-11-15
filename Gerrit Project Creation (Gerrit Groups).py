import git
import requests
from requests.auth import HTTPBasicAuth
from halo import Halo
import json
import sys
import urllib.parse
import os



'''
This script will automate the process of creating new gerrit projects with Gerrit groups access from a json file that contains one or more repositories.

Needed libraries:
requests==2.28.0
spinners==0.0.24
'''

# AUTHENTICATION
print("# AUTHENTICATION")
netid = input("Your netid: ") or os.environ["username env variable"]
token = input("Your Gerrit HTTPs Token: ") or os.environ["token env variable"]

# VARIABLES
spinner = Halo(text='Loading', spinner='dots')

# FUNCTIONS
def spinner_stop(str):
    spinner.stop()
    sys.stdout.flush()
    print(str)

# INPUT THE PROJECT(S) AND THE LDAP GROUPS FROM JSON
print("\n\n\n# IMPORTING THE PROJECT(S) INFORMATION FROM JSON FILE")
spinner.start()
projects_information =  "Projects.json"
with open(projects_information, "r") as f:
    all_projects = json.loads(f.read())
spinner_stop("--> DONE")


for projects in all_projects:
    for project in projects["projects"]:
        # REMOVING TRAILING SPACES AND REPLACING THE REST WITH UNDERSCORES IN THE PROJECT NAME
        project = project.strip(" ").replace(" ", "_")
        # CREATE THE NEW PROJECT
        print(f"\n\n\n# CREATING NEW PROJECT: {project}")
        # THIS IS THE PROJECT API ENDPOINT (WE NEED TO ESCAPE ANY POSSIBLE SLASHES BY ENCODING THE PROJECT NAME)
        project_endpoint = f"https://gerrit.com/a/projects/" + urllib.parse.quote(project, safe='')
        headers = {'Content-Type': 'application/json'}
        payload = projects["payload"]

        api_call = requests.request("PUT", project_endpoint, headers=headers, auth=HTTPBasicAuth(netid, token), data=json.dumps(payload))

        # EVALUATING THE API CALL RESPONSE
        if api_call.status_code == 201:
            spinner_stop("--> DONE")
        elif "already exists" in api_call.text:
            spinner_stop(f"--> Project '{project['name']}' already exists")
        else:
            spinner_stop(f"--> Error Creating Project '{project['name']}: {api_call.text}'")
