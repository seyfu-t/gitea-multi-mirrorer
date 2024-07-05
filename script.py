import requests
from urllib.parse import urlparse
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Environment variables
GITEA_TOKEN = os.getenv('GITEA_TOKEN')
GITEA_INSTANCE_URL = os.getenv('GITEA_INSTANCE_URL')

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

def get_gitlab_repos(user):
    repos = []
    page = 1
    while True:
        response = requests.get(f'https://gitlab.com/api/v4/users/{user}/projects?page={page}')
        if response.status_code != 200:
            raise Exception(f'Failed to fetch GitLab repos: {response.status_code}')
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

    response = requests.post(f"{GITEA_INSTANCE_URL}/api/v1/repos/migrate", json=payload, headers=headers)

    if response.status_code == 201:
        print(f"Successfully mirrored {repo_name}")
    else:
        print(f"Failed to create mirror for {repo_name}: {response.status_code} {response.text}")

def main():
    profile_url = input("Enter the profile URL: ").strip()
    parsed_url = urlparse(profile_url)
    
    if 'github.com' in parsed_url.netloc:
        source = 'github'
        user = parsed_url.path.strip('/')
        repos = get_github_repos(user)
    elif 'gitlab.com' in parsed_url.netloc:
        source = 'gitlab'
        user = parsed_url.path.strip('/')
        repos = get_gitlab_repos(user)
    else:
        print("Invalid source platform. Exiting.")
        return

    gitea_org = input("Enter the Gitea organization name: ").strip()

    for repo in repos:
        repo_name = f"{user}.{repo['name']}"
        clone_url = repo['clone_url']
        description = f"Mirror of {source}.com/{user}/{repo['name']}"
        create_gitea_mirror(clone_url, repo_name, gitea_org, description)

if __name__ == '__main__':
    main()
