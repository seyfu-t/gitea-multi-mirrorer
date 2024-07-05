# Gitea Multi-Mirrorer

Gitea Multi-Mirrorer is a Python script that allows you to mirror repositories from GitHub, GitLab, or any Gitea instance to your specified Gitea instance. This tool is useful for creating backups or maintaining mirrors of repositories across different platforms.

## Features

- Mirror repositories from GitHub, GitLab, and Gitea instances
- Support for GitLab groups and users
- Automatic handling of pagination for large numbers of repositories
- Configurable through environment variables

## Prerequisites

- Python 3.6+
- `requests` library
- `python-dotenv` library

## Installation

1. Clone this repository or download the script.
2. Install the required libraries:
pip install requests python-dotenv
3. Create a `.env` file in the same directory as the script with the following content:

```ini
GITEA_TOKEN=your_gitea_api_token
GITEA_INSTANCE_URL=https://your.gitea.instance
```

Replace `your_gitea_api_token` with your Gitea API token and `https://your.gitea.instance` with the URL of your Gitea instance.

## Usage

Run the script using Python:
```bash
python gitea_multi_mirrorer.py
```
The script will prompt you for:

1. The profile URL of the repositories you want to mirror (GitHub, GitLab, or Gitea)
2. The Gitea organization or username that will own the mirrored repositories

The script will then create mirrors of all repositories found at the given profile URL in your specified Gitea instance.

## Notes

- For GitLab, both user profiles and group URLs are supported.
- For Gitea instances, the script assumes a standard API structure. Some instances may require authentication for API access.
- The script uses the name format `{original_owner}.{repo_name}` for mirrored repositories to avoid naming conflicts.

## Contributing

Contributions, issues, and feature requests are welcome. Feel free to check [issues page](link_to_your_issues_page) if you want to contribute.

## License

[MIT](https://choosealicense.com/licenses/mit/)