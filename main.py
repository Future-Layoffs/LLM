import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        app="core.server:app",
        reload=True,
        host="127.0.0.1",
        port=8001,
        workers=1,
    )
