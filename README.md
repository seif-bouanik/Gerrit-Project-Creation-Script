# Gerrit Projects Creation Using Python Scripts
This repository has two scripts to cover two Gerrit project creation scenarios:
1. Projects that will inherit their permissions from **native Gerrit groups**.
2. Projects that will create these from scratch using internal **LDAP groups**.     

## PREREQUISITES
[Python3](https://www.python.org/downloads/) should be installed on your local machine. The following libraries should be installed using pip:   
```pip3 install requests GitPython spinners halo!```

You need to create an HTTPS token on Gerrit then save it to be used later:   
**Settings → HTTP Credentials → Generate New Password**

Finally, you need to clone this repository on your local machine:   
```git clone "https://gitgerrit.asux.aptiv.com/a/Gerrit_Automation_Script"```
   
## AUTHENTICATION
First, we need to need to configure authentication in the Python script, we can do this three ways:
1. hard code the credentials in the script like this by replacing the strings with your credentials:
```
#AUTHENTICATION
print("# AUTHENTICATION")
netid = "YOUR NETID" #Replace with your actual Netid
token = "YOUR GERRIT TOKEN" #Replace with your HTTPS token
```
2. Prompt you for the credentials every time you run the script:
```
# AUTHENTICATION
print("# AUTHENTICATION")
netid = input("Your netid: ")
token = input("Your Gerrit HTTPs Token: ")
```
3. Or a mix of the two, where it will prompt you for the credentials, but if you press enter, it will use the hard coded credentials in the script:
```
# AUTHENTICATION
print("# AUTHENTICATION")
netid = input("Your netid: ") or "YOUR NETID"
token = input("Your Gerrit HTTPs Token: ") or "YOUR GERRIT TOKEN"
```   

## SIMPLE GERRIT PROJECTS
To create simple Gerrit projects based on Gerrit groups or other projects, you will first need to fill out the project(s) information in the json file (*"Projects.json"*).   
You can put the projects names with the same config under *“projects”*.   
You can specify the projects configuration under “payload”, you can find out more about each configuration [here.](https://gerrit-review.googlesource.com/Documentation/rest-api-projects.html#project-input)   
```
[
	{
	"projects comment":  "Put the names of the all the projects you want to create with the same config in the 'projects' object below",
	"projects": [
		"Project1",
		"Project2"
		],
	"payload comment":  "Customize the config for the projects you want to create in the 'payload' object below, check all the possible configs here: https://gerrit-review.googlesource.com/Documentation/rest-api-projects.html#project-input",
	"payload": {
		"description":  "Project Description",
		"submit_type":  "INHERIT",
		"parent":  "Parent_Project",
		"create_empty_commit":  true,
		"branches": [
		"master",
		"dev"
		],
		"permissions_only":  false
		}
	}
]
```

In case you wanted to create projects in bulk, you can structure the json file to look like this:   
```
[
	{
		"Projects set #1"
	}
	{
		"Projects set #2"
	}
	{
		"Projects set #n"
	}
]
```
   
Finally, you can execute the script from your command line using:   
```python Gerrit Project Creation (Simple).py```

 
## LDAP-BASED PROJECTS
For projects that inherit access from LDAP groups, the projects config JSON looks something like this:   
```
[
	{
		"name": "Project_Title",
		"ldap_dev": "ldap/Access_group",
		"ldap_ci": "ldap/CI_Access_group"
	}
]
```
   
Where each project will have its name. and two LDAP groups names. To create in bulk, you can use the following structure:   
```
[
	{
		"Project #1"
	}
	{
		"Project #2"
	}
	{
		"Project #3"
	}
]
```
 
In case you need to customize the project details further, you can find the config inside the script under the variable name *“payload”*.   

To configure authentication and run the script, follow the same steps detailed above.   
