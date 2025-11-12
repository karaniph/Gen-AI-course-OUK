import os
import json
import shutil
from typing import Dict, Any
from .repo_mapper import RepoMapper
from .code_analyzer import CodeAnalyzer
from .doc_genie import DocGenie
from .llm_agent import LLMAgent
from .repo_utils import get_file_content

class CodeGenius:
    """
    The Code Genius (Supervisor) agent orchestrates the entire documentation
    generation workflow.
    """
    def __init__(self, clone_base_dir: str = "cloned_repos", output_dir: str = "documentation_output"):
        self.llm_agent = LLMAgent()
        self.repo_mapper = RepoMapper(clone_base_dir=clone_base_dir)
        self.code_analyzer = CodeAnalyzer()
        self.doc_genie = DocGenie(llm_agent=self.llm_agent)
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def generate_docs(self, repo_url: str) -> Dict[str, Any]:
        """
        Runs the full documentation generation pipeline for a given repository URL.
        """
        print(f"\n--- Starting Code Genius Workflow for {repo_url} ---")
        
        # 1. Repo Mapping
        repo_map_result = self.repo_mapper.map_repository(repo_url)
        if repo_map_result["status"] != "success":
            return repo_map_result

        local_path = repo_map_result["local_path"]
        repo_name = repo_map_result["repo_name"]
        
        # 2. Code Analysis (CCG Construction)
        print("\n--- Running Code Analyzer ---")
        
        # Simple filter for Python files
        python_files = [
            os.path.join(local_path, f) 
            for f in repo_map_result["file_tree"].keys() 
            if f.endswith(".py")
        ]
        
        for file_path in python_files:
            try:
                file_content = get_file_content(file_path)
                # We use the repo_name as a simple repo_id for now
                self.code_analyzer.analyze_file(file_path, file_content, repo_id=repo_name)
            except Exception as e:
                print(f"ERROR analyzing file {file_path}: {e}")

        # 3. Documentation Generation
        print("\n--- Running DocGenie ---")
        
        # Get the CCG relationships for the DocGenie
        ccg_relationships = self.code_analyzer.ccg_relationships
        
        # Generate Mermaid Diagram Code
        mermaid_code = self.doc_genie.generate_mermaid_diagram(ccg_relationships)
        mermaid_path = os.path.join(self.output_dir, f"{repo_name}_ccg.mmd")
        with open(mermaid_path, "w") as f:
            f.write(mermaid_code)
        print(f"INFO: Mermaid diagram code saved to {mermaid_path}")
        
        # Render Diagram to PNG (using the utility)
        diagram_path = os.path.join(self.output_dir, f"{repo_name}_ccg.png")
        try:
            os.system(f"manus-render-diagram {mermaid_path} {diagram_path}")
            print(f"INFO: Diagram rendered to {diagram_path}")
        except Exception as e:
            print(f"WARNING: Could not render diagram. Ensure 'manus-render-diagram' is in PATH. Error: {e}")
            diagram_path = None

        # Generate Markdown Documentation
        markdown_doc = self.doc_genie.generate_documentation(repo_map_result, ccg_relationships)
        markdown_path = os.path.join(self.output_dir, f"{repo_name}_documentation.md")
        with open(markdown_path, "w") as f:
            f.write(markdown_doc)
        print(f"INFO: Markdown documentation saved to {markdown_path}")
        
        # 4. Cleanup and Final Result
        shutil.rmtree(local_path)
        print(f"INFO: Cleaned up cloned repository at {local_path}")

        return {
            "status": "success",
            "repo_url": repo_url,
            "repo_name": repo_name,
            "markdown_path": markdown_path,
            "diagram_path": diagram_path,
            "mermaid_path": mermaid_path
        }

# Example usage for testing
if __name__ == '__main__':
    # Add the parent directory to the path for relative imports
    import sys
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    
    # NOTE: Use a small, public test repository with Python files
    TEST_REPO = "https://github.com/pallets/flask.git" # Flask is too large, let's use a smaller one
    TEST_REPO = "https://github.com/vslaykovsky/jac-example-project.git" # Has Python files
    
    genius = CodeGenius()
    result = genius.generate_docs(TEST_REPO)
    
    print("\n--- Final Result ---")
    print(json.dumps(result, indent=2))
