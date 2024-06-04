from pydantic import BaseModel
from fastapi import APIRouter,HTTPException,Depends
from app.controllers import ProcessController
import tempfile
from langchain_community.llms import Cohere
from langchain import PromptTemplate, LLMChain
from app.controllers import QuestionController, QuestionContext
from app.services.utils import ServerUtils
from core.shared_state import GlobalState

class Question(BaseModel):
    question: str

query_router=APIRouter()


@query_router.get("/", tags=["Query"])
async def health():
    return {"message": "Query working properly !!!"}


@query_router.post("/ask-question", tags=["Query"])
async def ask_question(request: Question, state: GlobalState = Depends(GlobalState)):
    g_github_url=state.get_github_url
    g_repo_name=state.get_repo_name
    
    
    if state.get_github_url() is None:
        raise HTTPException(status_code=400, detail="GitHub URL is not available. Call /process_repository first.")
    
    with tempfile.TemporaryDirectory() as local_path:
        clone = await ProcessController.clone_repository(state.get_github_url(), local_path)
        if clone:
            index, documents, file_type_counts, filenames = await ProcessController.load_and_index_files(local_path)
            if index is None:
                raise HTTPException(status_code=400, detail="No documents found to index.")
    
    user_input = request.question
    
    # Use Cohere instead of OpenAI
    cohere_api_key = '3gV8JUYV4oqWAk3CoueXew4J2Kpbi6fQTaK5Q0rv'
    model_name="command"
    llm = Cohere(cohere_api_key=cohere_api_key, model="command", temperature=0.6)

    template = """
    Repo: {repo_name} ({repo_name}) | Conv: {conversation_history} | Docs: {numbered_documents} | Q: {user_input} | FileCount: {file_type_counts} | FileNames: {filenames}

    Instr:
    1. Answer based on context/docs.
    2. Focus on repo/code.
    3. Consider:
        a. Purpose/features - describe.
        b. Functions/code - provide details/samples.
        c. Setup/usage - give instructions.
    4. Unsure? Say "I am not sure".
    Answer:
    """
 
    prompt = PromptTemplate(
        template=template,
        input_variables=["g_repo_name", "g_github_url", "conversation_history", "user_input", "numbered_documents", "file_type_counts", "filenames"]
    )

    llm_chain = LLMChain(prompt=prompt, llm=llm)

    conversation_history = ""
    question_context = QuestionContext(index, documents, llm_chain, model_name, g_repo_name, g_github_url, conversation_history, file_type_counts, filenames)

    user_input = ServerUtils.format_user_question(user_input)
    
    answer = await QuestionController.ask_question(user_input, question_context)
    
    return {"answer": answer}

