import requests
from urllib.parse import urlparse
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Environment variables
GITEA_TOKEN = os.getenv('GITEA_TOKEN')
GITEA_INSTANCE_URL = os.getenv('GITEA_INSTANCE_URL')

GITEA_API_URL = f'{GITEA_INSTANCE_URL}/api/v1'

def get_github_repos(user):
    repos = []
    page = 1
    while True:
        response = requests.get(f'https://api.github.com/users/{user}/repos?page={page}')
        if response.status_code != 200:
            raise Exception(f'Failed to fetch GitHub repos: {response.status_code}')
        data = response.json()
        if not data:
            break
        repos.extend(data)
        page += 1
    return repos

def get_gitlab_repos(path):
    repos = []
    page = 1
    
    # First, try to get repos assuming it's a group
    while True:
        response = requests.get(f'https://gitlab.com/api/v4/groups/{path}/projects?page={page}&per_page=100&include_subgroups=true')
        
        if response.status_code == 404:
            # If it's not a group, try as a user
            user_response = requests.get(f'https://gitlab.com/api/v4/users?username={path}')
            if user_response.status_code == 200 and user_response.json():
                user_id = user_response.json()[0]['id']
                response = requests.get(f'https://gitlab.com/api/v4/users/{user_id}/projects?page={page}&per_page=100')
            else:
                raise Exception(f'Neither user nor group found: {path}')
        
        if response.status_code != 200:
            raise Exception(f'Failed to fetch GitLab repos: {response.status_code}')
        
        data = response.json()
        if not data:
            break
        repos.extend(data)
        page += 1
    
    return repos

def get_gitea_repos(base_url, user):
    repos = []
    page = 1
    while True:
        response = requests.get(f'{base_url}/api/v1/users/{user}/repos?page={page}&limit=500')
        if response.status_code != 200:
            raise Exception(f'Failed to fetch Gitea repos: {response.status_code}')
        data = response.json()
        if not data:
            break
        repos.extend(data)
        page += 1
    return repos

def create_gitea_mirror(clone_addr, repo_name, repo_owner, description):
    headers = {
        'Authorization': f'Bearer {GITEA_TOKEN}',
        'Content-Type': 'application/json'
    }

    payload = {
        "clone_addr": clone_addr,
        "repo_name": repo_name,
        "repo_owner": repo_owner,
        "description": description,
        "lfs": True,
        "mirror": True,
        "wiki": True
    }

    response = requests.post(f"{GITEA_API_URL}/repos/migrate", json=payload, headers=headers)

    if response.status_code == 201:
        print(f"Successfully mirrored {repo_name}")
    else:
        print(f"Failed to create mirror for {repo_name}: {response.status_code} {response.text}")

def checkUserOrOrgExists(name: str):
    response = requests.get(f'{GITEA_API_URL}/users/{name}')
    return response.status_code == 200

def main():
    profile_url = input("Enter the profile URL: ").strip()
    parsed_url = urlparse(profile_url)
    
    if 'github.com' in parsed_url.netloc:
        source = 'github.com'
        user = parsed_url.path.strip('/')
        repos = get_github_repos(user)
        json_clone_url = 'clone_url'
    elif 'gitlab.com' in parsed_url.netloc:
        source = 'gitlab.com'
        user = parsed_url.path.strip('/')  # This will get the full path
        repos = get_gitlab_repos(user)
        json_clone_url = 'http_url_to_repo'
    elif parsed_url.path.count('/') >= 1:  # Assuming it's a Gitea URL if it has at least one slash in the path
        source = parsed_url.netloc
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
        user = parsed_url.path.split('/')[1]  # Get the username from the URL path
        repos = get_gitea_repos(base_url, user)
        json_clone_url = 'clone_url'
    else:
        print("Invalid source platform. Exiting.")
        return

    while True:
        gitea_org = input("Enter the Gitea organization or username, that will own the repo: ").strip()

        if not checkUserOrOrgExists(gitea_org):
            print("This user or organization does not exist")
        else:
            break

    for repo in repos:
        repo_name = f"{user}.{repo['name']}"
        clone_url = repo[json_clone_url]
        description = f"Mirror of {source}/{user}/{repo['name']}"
        create_gitea_mirror(clone_url, repo_name, gitea_org, description)

if __name__ == '__main__':
    main()
