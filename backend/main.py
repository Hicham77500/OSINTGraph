"""
OsintGraph — FastAPI Main Application
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import socketio
from dotenv import load_dotenv
import os

from routers import graph, transforms, workspaces

load_dotenv()

# Socket.IO server
sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🕵️  OsintGraph backend starting…")
    yield
    print("🛑  OsintGraph backend shutting down…")

app = FastAPI(
    title="OSINTGraph API",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS
origins = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Expose sio to routers
app.state.sio = sio

# Routers
app.include_router(graph.router, prefix="/graph", tags=["graph"])
app.include_router(transforms.router, prefix="/transforms", tags=["transforms"])
app.include_router(workspaces.router, prefix="/workspaces", tags=["workspaces"])

@app.get("/health")
async def health():
    return {"status": "ok", "service": "OSINTGraph"}

# Socket.IO events
@sio.event
async def connect(sid, environ):
    print(f"[WS] Client connected: {sid}")

@sio.event
async def disconnect(sid):
    print(f"[WS] Client disconnected: {sid}")

# Mount Socket.IO as ASGI app
asgi_app = socketio.ASGIApp(sio, other_asgi_app=app)
