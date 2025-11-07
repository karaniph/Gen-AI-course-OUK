import os
from openai import OpenAI

class LLMAgent:
    """
    The LLMAgent is responsible for all LLM interactions, such as summarization
    and eventually documentation generation.
    """
    def __init__(self):
        # The assignment mentions using OpenAI or Gemini. We will use the 
        # environment variable for the model name.
        # Use the pre-configured OpenAI client
        self.client = OpenAI()
        self.model = os.getenv("LLM_MODEL", "gemini-2.5-flash")

    def summarize_readme(self, readme_content: str) -> str:
        """
        Generates a concise summary of the README content.
        
        :param readme_content: The full text content of the README file.
        :return: A concise summary of the project.
        """
        if not readme_content:
            return "No README content provided for summarization."

        prompt = f"""
        You are an expert software documentation assistant. Your task is to read the
        following README file content and generate a concise, high-level summary of the
        project. The summary should be suitable for a project overview section in a
        technical report.

        README Content:
        ---
        {readme_content}
        ---

        CONCISE SUMMARY:
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert software documentation assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"Error during LLM summarization: {e}"

# Example usage for testing
if __name__ == '__main__':
    # Add the parent directory to the path for module imports
    import sys
    import os
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    
    # Dummy README content
    dummy_readme = """
    # Project X: The Ultimate Widget Generator
    
    ## Overview
    Project X is a highly scalable, cloud-native application designed to generate
    customizable widgets on demand. It uses a microservices architecture with
    a Python backend (Flask) and a React frontend. Data is stored in a PostgreSQL
    database.
    
    ## Installation
    1. Clone the repository.
    2. Run `pip install -r requirements.txt`.
    3. Set up the database with `init_db.sh`.
    
    ## Usage
    Start the server with `python app.py`. Navigate to http://localhost:5000.
    """
    
    agent = LLMAgent()
    summary = agent.summarize_readme(dummy_readme)
    
    print("\n--- LLM Summary Result ---")
    print(summary)
