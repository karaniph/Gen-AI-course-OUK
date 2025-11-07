import os
import shutil
import subprocess

def clone_repo(repo_url: str, clone_dir: str) -> str:
    """
    Clones a Git repository into a specified directory.
    If the directory already exists, it is removed first.
    
    :param repo_url: The URL of the Git repository.
    :param clone_dir: The local directory to clone into.
    :return: The path to the cloned repository directory.
    :raises subprocess.CalledProcessError: If the cloning fails.
    """
    if os.path.exists(clone_dir):
        shutil.rmtree(clone_dir)
        
    print(f"Cloning {repo_url} into {clone_dir}...")
    subprocess.run(["git", "clone", repo_url, clone_dir], check=True, capture_output=True, text=True)
    print("Cloning complete.")
    return clone_dir

def generate_file_tree(root_dir: str, ignore_dirs: list[str] = ['.git', '__pycache__', 'node_modules', '.venv', 'venv']) -> dict:
    """
    Traverses a directory and generates a structured representation of files and folders.
    
    :param root_dir: The root directory to start traversal.
    :param ignore_dirs: A list of directory names to ignore.
    :return: A dictionary representing the file tree.
    """
    tree = {}
    for entry in os.scandir(root_dir):
        if entry.name in ignore_dirs:
            continue
            
        if entry.is_dir():
            tree[entry.name] = generate_file_tree(entry.path, ignore_dirs)
        elif entry.is_file():
            # Store file path relative to the root_dir for later use
            relative_path = os.path.relpath(entry.path, root_dir)
            tree[entry.name] = relative_path
            
    return tree

def get_file_content(file_path: str) -> str:
    """
    Reads the content of a file.
    
    :param file_path: The absolute or relative path to the file.
    :return: The content of the file as a string.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {e}"

# Example usage (for testing purposes)
if __name__ == '__main__':
    # This part is for local testing and won't run when imported by Jac
    TEST_REPO = "https://github.com/vslaykovsky/jac-example-project"
    CLONE_PATH = "./test_repo_clone"
    
    try:
        cloned_path = clone_repo(TEST_REPO, CLONE_PATH)
        file_tree = generate_file_tree(cloned_path)
        print("\nGenerated File Tree:")
        import json
        print(json.dumps(file_tree, indent=2))
        
        # Clean up
        shutil.rmtree(CLONE_PATH)
    except subprocess.CalledProcessError as e:
        print(f"Git Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
