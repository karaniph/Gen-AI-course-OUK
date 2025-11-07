import os
from git import GitCommandError
from .repo_utils import clone_repo, generate_file_tree, get_file_content
from .llm_agent import LLMAgent

class RepoMapper:
    """
    The RepoMapper agent is responsible for cloning the target repository
    and generating a structured file-tree representation.
    """
    def __init__(self, clone_base_dir: str = "cloned_repos"):
        self.clone_base_dir = clone_base_dir
        os.makedirs(self.clone_base_dir, exist_ok=True)
        self.llm_agent = LLMAgent()

    def map_repository(self, repo_url: str) -> dict:
        """
        Clones the repository and generates the file tree.

        :param repo_url: The URL of the Git repository.
        :return: A dictionary containing the repository metadata and file tree.
        """
        repo_name = repo_url.split('/')[-1].replace('.git', '')
        clone_dir = os.path.join(self.clone_base_dir, repo_name)

        try:
            local_path = clone_repo(repo_url, clone_dir)
        except GitCommandError as e:
            print(f"ERROR: Failed to clone repository: {e}")
            return {
                "status": "error",
                "message": f"Failed to clone repository: {e}",
                "repo_url": repo_url
            }
        except Exception as e:
            print(f"ERROR: An unexpected error occurred during cloning: {e}")
            return {
                "status": "error",
                "message": f"Unexpected error during cloning: {e}",
                "repo_url": repo_url
            }

        file_tree = generate_file_tree(local_path)

        result = {
            "status": "success",
            "repo_url": repo_url,
            "repo_name": repo_name,
            "local_path": local_path,
            "file_tree": file_tree
        }

        # 4. Summarize the README
        readme_path = os.path.join(local_path, "README.md")
        readme_summary = ""
        if os.path.exists(readme_path):
            readme_content = get_file_content(readme_path)
            readme_summary = self.llm_agent.summarize_readme(readme_content)
        
        # Add the summary to the result
        result["readme_summary"] = readme_summary

        return result

# Example usage for testing
if __name__ == '__main__':
    # Add the parent directory to the path for relative imports
    import sys
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))
    
    # NOTE: Use a small, public test repository
    TEST_REPO = "https://github.com/pallets/flask.git"
    
    mapper = RepoMapper()
    mapping_result = mapper.map_repository(TEST_REPO)
    
    import json
    print("\n--- Repo Mapping Result ---")
    print(json.dumps(mapping_result, indent=2))
    
    # Clean up the cloned directory after inspection
    if mapping_result.get("status") == "success":
        import shutil
        shutil.rmtree(mapping_result["local_path"])
        print(f"\nCleaned up {mapping_result['local_path']}")
