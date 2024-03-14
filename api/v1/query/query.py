from fastapi import APIRouter

query_router=APIRouter()


@query_router.get("/", tags=["Query"])
async def health():
    return {"message": "Query API working properly !!!"}


@query_router.post("/ask-question", tags=["Query"])
async def ask_question():
    return {"message": "Asking Question API working properly !!!"}
