from fastapi import FastAPI
import asyncio
import random


app = FastAPI(title="External Simulator")


@app.post("/result")
async def result() -> dict:
    delay = random.uniform(0, 60)
    await asyncio.sleep(delay)
    return {"success": bool(random.getrandbits(1))}


