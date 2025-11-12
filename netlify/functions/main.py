import os
import shutil
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from mangum import Mangum

# Add the project root to the path so we can import codebase_genius
# This is crucial for Netlify functions to find the package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from codebase_genius import CodeGenius

# Initialize FastAPI app
app = FastAPI(
    title="Codebase Genius API",
    description="AI-powered multi-agent system for generating software documentation."
)

# Initialize the Supervisor Agent
# Note: In a serverless environment, this initialization happens on every cold start.
genius = CodeGenius()

class RepoURL(BaseModel):
    repo_url: str

@app.get("/")
async def root():
    return {"message": "Welcome to Codebase Genius API. Use /docs for API documentation."}

@app.post("/generate_docs")
async def generate_documentation(repo_url_data: RepoURL):
    """
    Triggers the documentation generation process for a given GitHub repository URL.
    """
    repo_url = repo_url_data.repo_url
    
    # Run the CodeGenius workflow
    result = genius.generate_docs(repo_url)
    
    if result["status"] != "success":
        raise HTTPException(status_code=500, detail=result["message"])
    
    # Return the result with links to download the files
    repo_name = result["repo_name"]
    
    # Read the generated Markdown content
    with open(result["markdown_path"], "r") as f:
        markdown_content = f.read()
        
    # Clean up the output directory after reading the file
    shutil.rmtree(genius.output_dir)
    os.makedirs(genius.output_dir, exist_ok=True)

    return {
        "status": "success",
        "repo_name": repo_name,
        "markdown_documentation": markdown_content,
        "diagram_note": "Diagram is generated but cannot be served directly from a serverless function response. Use the local version or a dedicated file storage service for the final diagram file."
    }

# Wrap the FastAPI app with Mangum for Netlify Functions
handler = Mangum(app)
