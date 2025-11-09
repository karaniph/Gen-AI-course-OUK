import os
import re
# from tree_sitter import Language, Parser # Commented out due to environment issues

# --- CCG Data Structures ---

class CCGNode:
    """Represents a node in the Code Context Graph (CCG)."""
    def __init__(self, node_type: str, name: str, file_path: str, start_line: int):
        self.node_type = node_type  # e.g., 'module', 'class', 'function'
        self.name = name
        self.file_path = file_path
        self.start_line = start_line
        self.attributes = {}
        self.relationships = []  # List of (relationship_type, target_node_id)

    def __repr__(self):
        return f"<{self.node_type}:{self.name} in {os.path.basename(self.file_path)}>"

class CCGRelationship:
    """Represents a directed edge in the CCG."""
    def __init__(self, source_id: str, target_id: str, rel_type: str):
        self.source_id = source_id
        self.target_id = target_id
        self.rel_type = rel_type  # e.g., 'calls', 'inherits', 'contains'

    def __repr__(self):
        return f"({self.source_id}) -[{self.rel_type}]-> ({self.target_id})"

class CodeAnalyzer:
    """
    The CodeAnalyzer agent is responsible for parsing source files and
    constructing the Code Context Graph (CCG).
    """
    def __init__(self, grammar_dir: str = "tree-sitter-grammars"):
        self.grammar_dir = grammar_dir
        self.parsers = {}
        self.ccg_nodes = {}  # {node_id: CCGNode}
        self.ccg_relationships = [] # [CCGRelationship]
        self.node_counter = 0
        
        self._load_languages()

    def _load_languages(self):
        """Mocks Tree-sitter loading due to environment issues."""
        print("WARNING: Tree-sitter initialization skipped due to environment issues. Using regex-based parsing for now.")
        self.parsers['.py'] = 'MOCKED_PARSER' # Placeholder for the parser object

    def analyze_file(self, file_path: str, file_content: str, repo_id: str):
        """Parses a single file and extracts CCG nodes and relationships."""
        _, ext = os.path.splitext(file_path)
        parser = self.parsers.get(ext)
        
        if not parser:
            # print(f"WARNING: No parser available for file type: {ext}")
            return

        # --- CCG Construction Logic (Regex-based Mock) ---
        
        # 1. Create a node for the module itself
        module_name = os.path.basename(file_path).replace(ext, "")
        module_id = self.get_next_node_id()
        module_node = CCGNode(
            node_type="module",
            name=module_name,
            file_path=file_path,
            start_line=1
        )
        self.ccg_nodes[module_id] = module_node
        
        # 2. Find function and class definitions
        lines = file_content.splitlines()
        
        # Regex for finding definitions (simplified)
        def_regex = re.compile(r"^(?:class|def)\s+(\w+)")
        
        # Store definitions to associate calls later
        definitions = []
        
        for i, line in enumerate(lines):
            match = def_regex.match(line.strip())
            if match:
                def_type = "class" if line.strip().startswith("class") else "function"
                def_name = match.group(1)
                def_id = self.get_next_node_id()
                
                def_node = CCGNode(
                    node_type=def_type,
                    name=def_name,
                    file_path=file_path,
                    start_line=i + 1
                )
                self.ccg_nodes[def_id] = def_node
                definitions.append({"id": def_id, "name": def_name, "start_line": i + 1})
                
                # Relationship: Module contains definition
                self.ccg_relationships.append(CCGRelationship(
                    source_id=module_id,
                    target_id=def_id,
                    rel_type="contains"
                ))
        
        # 3. Find function calls and associate them with the containing definition
        call_regex = re.compile(r"(\w+)\s*\(")
        
        # Simple association: associate call with the definition that starts before it
        # This is a highly simplified mock for call graph construction
        for i, line in enumerate(lines):
            line_num = i + 1
            
            # Find the most recent definition that contains this line
            current_def_id = module_id
            current_def_name = module_name
            for d in reversed(definitions):
                if line_num >= d["start_line"]:
                    current_def_id = d["id"]
                    current_def_name = d["name"]
                    break
            
            call_matches = call_regex.findall(line)
            
            for call_name in call_matches:
                # Avoid self-referential calls and common keywords
                if call_name not in [current_def_name, "def", "class", "return", "if", "for", "while", "with", "try", "except", "print", "self"]:
                    # We don't know the target ID yet, so we store the name
                    self.ccg_relationships.append(CCGRelationship(
                        source_id=current_def_id,
                        target_id=call_name, # Storing name instead of ID for later resolution
                        rel_type="calls"
                    ))
                        
        print(f"INFO: CCG nodes and relationships extracted for {file_path}")

    def get_next_node_id(self) -> str:
        """Generates a unique ID for a new CCG node."""
        self.node_counter += 1
        return f"N{self.node_counter}"

    def query_ccg(self, query: str) -> list[CCGRelationship]:
        """
        Queries the CCG for relationships based on a simple string query.
        Example query: "Which functions call <function_name>?"
        
        :param query: The name of the function being called.
        :return: A list of CCGRelationship objects that call the target function.
        """
        target_name = query.strip().lower()
        
        # Simple implementation: find all 'calls' relationships where the target name matches
        results = []
        for rel in self.ccg_relationships:
            if rel.rel_type == "calls" and rel.target_id.lower() == target_name:
                # Resolve the source ID to get the actual node name
                source_node = self.ccg_nodes.get(rel.source_id)
                if source_node:
                    # Create a new relationship object with the resolved source name
                    results.append(CCGRelationship(
                        source_id=source_node.name,
                        target_id=rel.target_id,
                        rel_type=rel.rel_type
                    ))
        return results

# Example usage for testing
if __name__ == '__main__':
    # Add the parent directory to the path for module imports
    import sys
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    
    # Create a dummy Python file for testing
    dummy_file_path = "temp_test.py"
    dummy_content = """
def func_a(x):
    return x + 1

class MyClass:
    def method_b(self, y):
        return func_a(y)
"""
    with open(dummy_file_path, "w") as f:
        f.write(dummy_content)

    analyzer = CodeAnalyzer(grammar_dir="../tree-sitter-grammars")
    analyzer.analyze_file(dummy_file_path, dummy_content, repo_id="test_repo")
    
    print("\n--- CCG Nodes ---")
    for node_id, node in analyzer.ccg_nodes.items():
        print(f"{node_id}: {node}")
        
    print("\n--- CCG Relationships (Raw) ---")
    for rel in analyzer.ccg_relationships:
        print(rel)
        
    print("\n--- CCG Query: Who calls func_a? ---")
    query_results = analyzer.query_ccg("func_a")
    for rel in query_results:
        print(rel)
    
    os.remove(dummy_file_path)
