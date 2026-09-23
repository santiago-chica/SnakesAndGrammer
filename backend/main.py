from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api.games import router as games_router
from backend.api.websocket import router as websocket_router

app = FastAPI(title="Snakes & Ladders: Grammar Edition")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.include_router(games_router, prefix="/api/games", tags=["games"])
app.include_router(websocket_router, tags=["websocket"])

@app.get("/health")
def health():
    return {"status": "ok"}
