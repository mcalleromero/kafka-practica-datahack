from fastapi import FastAPI

from .collect import collect

app = FastAPI()


@app.get("/tweets")
async def tweets():
    return collect()
