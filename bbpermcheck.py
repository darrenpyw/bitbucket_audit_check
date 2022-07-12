import argparse
import requests
import json

"""
Author: Darren Pang
Emai: darrenpy@gmail.com

usage: bbpermcheck.py [options]

Bitbucket Permissions Audit Script

optional arguments:
-h, --help            show this help message and exit
-u USER               Project Admin username
-p PASSWORD           Project Admin password
-b BASEURL            Bitbucket host:port, default to http://127.0.0.1:7990
-m [MEMBERS [MEMBERS ...]]
                      List of team member names e.g. John David Joe
-g [GROUPS [GROUPS ...]]
                      List of group names e.g. ProjectGroupA ProjectGroupB

If no members or groups supplied, the script will list ALL repositoy users and
groups permission

"""
def printNoPermission(user):
    print(f'-- NAME: {user}   PERMISSION: NONE')

def printPermission(user, permission):
    print(f'++ NAME: {user}   PERMISSION: {permission}')

def get_repoGroups(args, key, slug):
    url = f'/rest/api/1.0/projects/{key}/repos/{slug}/permissions/groups'
    r = get_api(args, url)
    return r

def get_repoUsers(args, key, slug):
    url = f'/rest/api/1.0/projects/{key}/repos/{slug}/permissions/users'
    r = get_api(args, url)
    return r

def get_repos(args, key):
    url = f'/rest/api/1.0/projects/{key}/repos'
    r = get_api(args, url)
    return r
 
def get_projects(args):
    url = '/rest/api/1.0/projects'
    r = get_api(args, url)
    return r

def get_api(args,url):
    try:
        r = requests.get(
            args.baseurl + url,
            auth = (args.user, args.password)
            )
    except Exception :
        exit('Error connecting to the BitBucket URL. Please check the provided base URL.')
    
    if r.status_code == 401:
        exit('Wrong credentials. Please try again')
    elif r.status_code == 200:
        return r.json()
    else:
        exit(f'Unknown error: HTTP Status {r.status_code}')


def main():
    parser = argparse.ArgumentParser(
            description='Bitbucket Permissions Audit Script',
            usage='%(prog)s [options]',
            epilog='If no members or groups supplied, the script will list ALL repositoy users and groups permission'
            )
    parser.add_argument('-u', dest='user', required=True, help='Project Admin username')
    parser.add_argument('-p', dest='password', required=True, help='Project Admin password')
    parser.add_argument('-b', dest='baseurl', default='http://localhost:7990', help='Bitbucket host:port, default to http://127.0.0.1:7990')
    parser.add_argument('-m', dest='members', nargs='*', help='List of team member names e.g. John David Joe')
    parser.add_argument('-g', dest='groups', nargs='*', help='List of group names e.g. ProjectGroupA ProjectGroupB')

    args = parser.parse_args()
    
    # Get all projects for current user
    projects = get_projects(args) 
    for project in projects['values']:
        print('\nProject Name: ', project['name'])
        print('Public Access: ', 'YES' if project['public'] else 'NO')
        
        # Get all repositories for every project 
        repos = get_repos(args, project['key'])
        for repo in repos['values']:
            print('\n> Repository Name: ' + repo['name'])
            print('> Public Access: ', 'YES' if repo['public'] else 'NO')
            
            # Get all users with access to the repository
            users = get_repoUsers(args, project['key'], repo['slug'])
            
            # Get all groups with access to the repository
            groups = get_repoGroups(args, project['key'], repo['slug'])
           
            # Audit supplied users permission to the repository
            if args.members is not None:
                print('\n>> Audtiting supplied repository users permission')
                for auditUser in args.members:
                    result = list(filter(lambda u:u['user']['name'] == auditUser, users['values']))
                    if len(result) == 0:
                        printNoPermission(auditUser)
                    else:
                        u = dict(result[0])
                        printPermission(u['user']['name'], u['permission'])

            # Audit supplied groups permission to the repository
            if args.groups is not None:
                print('\n>> Audtiting supplied repository groups permission')
                for auditGroup in args.groups:
                    result = list(filter(lambda g:g['group']['name'] == auditGroup, groups['values']))
                    if len(result) == 0:
                        printNoPermission(auditGroup)
                    else:
                        g = dict(result[0])
                        printPermission(g['group']['name'], g['permission'])

            # If no arguments supplied, show all users and groups permission to the repository
            if args.members is None and args.groups is None:
                print('\n>> Showing ALL repository users permission')
                for user in users['values']:
                    printPermission(user['user']['name'], user['permission'])
                
                print('\n>> Showing ALL repository groups permission')
                for group in groups['values']:
                    printPermission(group['group']['name'], group['permission'])
            

if __name__ == "__main__":
    main()
