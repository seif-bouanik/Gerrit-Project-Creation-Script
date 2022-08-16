import git
import requests
from requests.auth import HTTPBasicAuth
from halo import Halo
import json
import re
import os
import sys
import urllib.parse
import pathlib
import shutil
import stat



'''
This script will automate the process of creating new gerrit projects with LDAP groups access from a json file that contains one or more repositories.

Needed libraries:
GitPython==3.1.27
requests==2.28.0
spinners==0.0.24
'''


# AUTHENTICATION
print("# AUTHENTICATION")
netid = input("Your netid: ") or "hardcoded netid"
token = input("Your Gerrit HTTPs Token: ") or "hardcoded token"


# VARIABLES
project_template = "All-project-template"
project_template_url = f"https://{netid}:{token}@gerrit.com/a/{project_template}"
workdir = str(pathlib.Path(__file__).parent.resolve())+"\\"
template_folder = "template\\"
meta_branch = "refs/meta/config"
meta_branch_remote = "refs/remotes/origin/meta/config"
spinner = Halo(text='Loading', spinner='dots')


# FUNCTIONS
def workdir_cleanup(folder):
    for root, dirs, files in os.walk(folder):
        for dir in dirs:
            os.chmod(os.path.join(root, dir), stat.S_IRWXU)
        for file in files:
            os.chmod(os.path.join(root, file), stat.S_IRWXU)
    shutil.rmtree(folder)

def spinner_stop(str):
    spinner.stop()
    sys.stdout.flush()
    print(str)

# INPUT THE PROJECT(S) AND THE LDAP GROUPS FROM JSON
print("\n\n\n# IMPORTING THE PROJECT(S) INFORMATION FROM JSON FILE")
spinner.start()
json_file = "Projects_ldap.json"
with open(json_file, "r") as f:
    projects_db = json.loads(f.read())
spinner_stop("--> DONE")


# CLONE THE TEMPLATE PROJECT & PULL THE META/CONFIG
print("\n\n\n# CLONING THE TEMPLATE PROJECT & PULLING THE META/CONFIG BRANCH")
print(f"PROJECT TEMPLATE: {project_template}")
print(f"CLONING TO: {workdir}{template_folder}")
spinner.start()
git.Repo.clone_from(project_template_url, template_folder)
template_repository = git.Git(template_folder)
template_repository.pull('origin', f"{meta_branch}:{meta_branch_remote}", "--allow-unrelated-histories")
spinner_stop("--> DONE")


for project in projects_db:
    # REMOVING TRAILING SPACES AND REPLACING THE REST WITH UNDERSCORES IN THE PROJECT NAME
    project['name'] = project['name'].strip(" ").replace(" ", "_")
    # CREATE THE NEW PROJECT
    print("\n\n\n" + "#"*25 + f"  PROJECT: {project['name']}  " + "#"*25)
    print("\n# CREATING THE NEW PROJECT")
    print(f"PROJECT: {project['name']}")
    print(f"LDAP DEV GROUP: {project['ldap_dev']}")
    print(f"LDAP CI GROUP: {project['ldap_ci']}")
    spinner.start()
    # THIS IS THE PROJECT URL FOR GIT OPERATIONS
    project_url = f"https://{netid}:{token}@gerrit.com/a/{project['name']}"
    # THIS IS THE PROJECT API ENDPOINT (WE NEED TO ESCAPE ANY POSSIBLE SLASHES BY ENCODING THE PROJECT NAME)
    project_api_endpoint = f"https://gerrit.com/a/projects/" + urllib.parse.quote(project['name'], safe='')
    headers = {'Content-Type': 'application/json'}
    # TO SEE ALL POSSIBLE OPTIONS FOR THE PAYLOAD, CHECK THE FOLLOWING LINK: https://gerrit-review.googlesource.com/Documentation/rest-api-projects.html#project-input
    payload = {
        "project": project['name'],
        # "description": "Project Description",
        "submit_type": "INHERIT",
        # "create_empty_commit": False,
        # "permissions_only": True,
        "owners": [
            project['ldap_dev'],
            project['ldap_ci']
        ]
        # "branches": [
        #     "master",
        #     "dev"
        # ]
    }
    
    api_call = requests.request("PUT", project_api_endpoint, headers=headers, auth=HTTPBasicAuth(netid, token), data=json.dumps(payload))

    # EVALUATING THE API CALL RESPONSE
    if api_call.status_code==201:
        spinner_stop("--> DONE")
    elif "already exists" in api_call.text:
        spinner_stop(f"--> Project '{project['name']}' already exists")
    else:
        spinner_stop(f"--> Error Creating Project '{project['name']}: {api_call.text}'")


    # CLONE THE NEW PROJECT
    print("\n\n\n# CLONING THE NEW PROJECT")
    project_folder = project['name'].split("/")[-1]
    print(f"PROJECT: {project['name']}")
    print(f"CLONING TO: {workdir}{project_folder}")  
    spinner.start()
    git.Repo.clone_from(project_url, project_folder)
    project_repository = git.Git(project_folder)  
    project_repository.pull('origin', f"{meta_branch}:{meta_branch_remote}", "--allow-unrelated-histories")
    spinner_stop("--> DONE")


    # APPEND THE TEMPLATE GROUPS TO THE NEW PROJECT GROUPS
    print("\n\n\n# APPENDING THE TEMPLATE GROUPS TO THE NEW PROJECT GROUPS")
    print(f"GROUPS FILE: {workdir}{project_folder}\groups") 
    spinner.start()
    with open(f"{template_folder}/groups", 'r') as template, open(f"{project_folder}\groups", 'a+') as project_groups_content: 
        template_groups_content = template.readlines()
        for line in template_groups_content[2:]:
            project_groups_content.write(line)
    spinner_stop("--> DONE")


    # MODIFY THE NEW PROJECT CONFIG FILE WITH LDAP GROUPS
    print("\n\n\n# MODIFYING THE NEW PROJECT CONFIG FILE WITH LDAP GROUPS")
    print(f"PROJECT CONFIG FILE: {workdir}{project_folder}\project.config")
    spinner.start()
    with open(f"{template_folder}project.config", 'r') as template, open(f"{project_folder}\project.config", 'w') as project_config: 
        template_config_content = template.read()
        project_config_content = re.sub('Temporal$', project['ldap_dev'], template_config_content, flags=re.M)
        project_config_content = re.sub('Temporal_CI$', project['ldap_ci'], project_config_content, flags=re.M)
        project_config.write(project_config_content)
    spinner_stop("--> DONE")


    # PUSH THE CHANGES TO THE META/CONFIG
    print("\n\n\n# PUSHING THE CHANGES (GROUPS) TO THE META/CONFIG BRANCH")
    commit_msg = "Updating Groups"
    file = "groups"
    print(f"ADDING FILE: {file}")
    print(f"COMMIT MESSAGE: {commit_msg}")
    print(f"DESTINATION BRANCH: {meta_branch}")
    spinner.start()
    project_repository = git.Repo(project_folder) 
    project_repository.git.add(file)
    project_repository.index.commit(commit_msg)
    project_repository.git.push("origin", f"HEAD:{meta_branch}")
    spinner_stop("--> DONE")


    print("\n\n\n# PUSHING THE CHANGES (CONFIG) TO THE META/CONFIG BRANCH")
    commit_msg = "Updating Project Config"
    file = "project.config"
    print(f"ADDING FILE: {file}")
    print(f"COMMIT MESSAGE: {commit_msg}")
    print(f"DESTINATION BRANCH: {meta_branch}")
    spinner.start()
    project_repository.git.add(file)
    project_repository.index.commit(commit_msg)
    project_repository.git.push("origin", f"HEAD:{meta_branch}")
    spinner_stop("--> DONE")
    print("\n\n\n")


# CLEAN UP THE PROJECT FOLDER
print("\n\n\n# CLEANING UP THE WORKDIR")
spinner.start()
workdir_cleanup(template_folder)
spinner_stop("--> DONE")