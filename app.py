from fastapi import FastAPI

app = FastAPI(
    title="Python 3.14 Template API",
    description="minimalistic backbone",
    version="0.1.0"
)

@app.get("/")
async def health_check():
    """
    Simple healthcheck endpoint. 
    Nice to check the availability of the Docker-Container.
    """
    return {
        "status": "ok", 
        "message": "The Python 3.14 Container is runnig"
    }
