from fastapi import APIRouter,HTTPException,Body
import tempfile
from pydantic import BaseModel
from app.controllers import ProcessController

class ProcessRepositoryRequest(BaseModel):
    github_url: str  


process_router=APIRouter()
g_github_url = None  
g_repo_name = None  


@process_router.get("/", tags=["Process"])
async def health():
    return {"message": "Process working properly !!!"}


@process_router.post("/process_repository", tags=["Process"])
async def process_repository(request: ProcessRepositoryRequest):
    global g_github_url,g_repo_name
    print(request)
    github_url=request.github_url
    # github_url = request.get("github_url")
    
    if not github_url:
        raise HTTPException(status_code=400, detail="github_url is required.")
    print(github_url)

    
    g_github_url = github_url
    repo_name = github_url.split("/")[-1]
    g_repo_name = repo_name
    
    with tempfile.TemporaryDirectory() as local_path:
        print(local_path);
        clone=await ProcessController.clone_repository(github_url, local_path)
        if clone:  
            index, documents, file_type_counts, filenames = await ProcessController.load_and_index_files(local_path)
            if index is None:
                raise HTTPException(status_code=400, detail="No documents found to index.")

    return {"message": "Repository processed successfully."}
      
    