import os
import json
from typing import Dict, Any, List
from .llm_agent import LLMAgent
from .code_analyzer import CCGRelationship

class DocGenie:
    """
    The DocGenie agent is responsible for generating the final documentation
    in Markdown format, including a diagram based on the CCG.
    """
    def __init__(self, llm_agent: LLMAgent):
        self.llm_agent = llm_agent

    def generate_mermaid_diagram(self, relationships: List[CCGRelationship]) -> str:
        """
        Generates a Mermaid graph definition from the CCG relationships.
        
        :param relationships: A list of CCGRelationship objects.
        :return: A string containing the Mermaid graph definition.
        """
        mermaid_code = ["graph TD"]
        
        # Use a set to store unique nodes and avoid duplicate definitions
        nodes = set()
        
        for rel in relationships:
            # Clean up node names for Mermaid (replace special chars)
            source_name = rel.source_id.replace(":", "_").replace(".", "_")
            target_name = rel.target_id.replace(":", "_").replace(".", "_")
            
            # Add nodes to the set
            nodes.add(f'{source_name}["{rel.source_id}"]')
            nodes.add(f'{target_name}["{rel.target_id}"]')
            
            # Add relationship
            mermaid_code.append(f'  {source_name} -->|{rel.rel_type}| {target_name}')

        # Add all unique nodes to the beginning of the code
        mermaid_code[1:1] = list(nodes)
        
        return "\n".join(mermaid_code)

    def generate_documentation(self, repo_map_result: Dict[str, Any], ccg_relationships: List[CCGRelationship]) -> str:
        """
        Generates the final Markdown documentation using the LLM.
        
        :param repo_map_result: The result from the RepoMapper.
        :param ccg_relationships: The relationships from the CodeAnalyzer.
        :return: The final Markdown documentation string.
        """
        
        # 1. Prepare the CCG summary for the LLM
        ccg_summary = "\n".join([str(rel) for rel in ccg_relationships])
        
        # 2. Prepare the file tree for the LLM
        file_tree_str = json.dumps(repo_map_result.get("file_tree", {}), indent=2)
        
        # 3. Construct the prompt
        prompt = f"""
        You are DocGenie, an expert technical writer. Your task is to generate a
        comprehensive Markdown documentation for a software project based on the
        provided information.

        **Project Overview (from README Summary):**
        {repo_map_result.get("readme_summary", "No summary available.")}

        **Repository Structure (File Tree):**
        ```json
        {file_tree_str}
        ```

        **Code Context Graph (CCG) Relationships:**
        The following is a list of key relationships (calls, contains) between code elements:
        ```
        {ccg_summary}
        ```

        **Instructions:**
        1.  Start with a clear **Project Summary** based on the README.
        2.  Include a section on **Code Architecture** that explains the main components (modules, classes, functions) and their relationships, using the CCG data.
        3.  Provide a **File Structure** section based on the file tree.
        4.  The documentation must be high-quality, professional, and easy to read.
        5.  Do NOT include the raw JSON or CCG relationships in the final output, only use them to inform your writing.
        """
        
        try:
            # Use the LLM to generate the documentation
            response = self.llm_agent.client.chat.completions.create(
                model=self.llm_agent.model,
                messages=[
                    {"role": "system", "content": "You are DocGenie, an expert technical writer. Generate comprehensive Markdown documentation."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"Error during documentation generation: {e}"

# Example usage for testing (will be integrated into the Supervisor later)
if __name__ == '__main__':
    # This part will be tested in the Supervisor phase
    print("DocGenie class defined. Testing will occur in the Supervisor phase.")
