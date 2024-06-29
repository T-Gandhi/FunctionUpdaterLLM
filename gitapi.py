import os
import subprocess
import requests
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

class GitHubAPI:
    def __init__(self):
        self.token = os.getenv("GH_TOKEN")
        if not self.token:
            raise ValueError("GitHub token not found. Please set GH_TOKEN in the .env file.")
        self.headers = {
            'Authorization': f'token {self.token}',
        }

    def clone_repo(self, repo_url, clone_dir=None):
        """
        Clones a GitHub repository given its URL and returns the path to the cloned directory.
        """
        if not repo_url:
            raise ValueError("Repository URL must be provided.")

        # get name of the repository from the URL and clone directory name
        repo_name = repo_url.split('/')[-1].replace('.git', '')
        if clone_dir:
            clone_path = os.path.join(clone_dir, repo_name)
        else:
            clone_path = os.path.join(os.getcwd(), repo_name)

        # Check if the directory exists and is not empty
        if os.path.exists(clone_path) and os.listdir(clone_path):
            print(f"Directory '{clone_path}' already exists and is not empty. Skipping cloning.")
            return clone_path

        # Run the git clone command
        try:
            subprocess.run(['git', 'clone', repo_url, clone_path], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error cloning repository: {e}")
            return None

        print(f"Repository cloned to: {clone_path}")
        return clone_path

# Example usage
if __name__ == "__main__":
    github_api = GitHubAPI()
    repo_url = "https://github.com/t-gandhi-19/example"  # Replace with the actual repository URL
    cloned_path = github_api.clone_repo(repo_url)

