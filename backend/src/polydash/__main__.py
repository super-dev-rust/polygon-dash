import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import node, block, dashboard
from .db import start_db
from .block_retriever.retriever import start_retriever
from .rating.live_time_heuristic import start_live_time_heuristic
from .rating.live_time_heuristic_a import start_live_time_heuristic_a

# Modules set up
start_db()
start_retriever()
start_live_time_heuristic()
start_live_time_heuristic_a()

# FastAPI set up
app = FastAPI()
app.include_router(node.router)
app.include_router(block.router)
app.include_router(dashboard.router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


@app.get("/")
async def root():
    return {"message": "Nothing here"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5500)
