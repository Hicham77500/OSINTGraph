"""
OSINTGraph — FastAPI Main Application
"""
import logging
from contextlib import asynccontextmanager

import os
import socketio
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from db.domain_client import domain_client
from middleware.auth import AuthMiddleware
from middleware.rate_limit import RateLimitMiddleware
from routers import graph, transforms, workspaces
from routers.api_v1 import router as api_v1_router

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("osintgraph")

sio = socketio.AsyncServer(
    async_mode="asgi",
    cors_allowed_origins=os.getenv("CORS_ORIGINS", "http://localhost:5173").split(","),
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("OSINTGraph backend starting")
    db_path = os.getenv("SQLITE_PATH", "osintgraph.db")
    db_dir = os.path.dirname(os.path.abspath(db_path))
    if db_dir:
        os.makedirs(db_dir, exist_ok=True)
    await domain_client.init_schema()
    await domain_client.ensure_default_dossier()
    yield
    logger.info("OSINTGraph backend shutting down")


app = FastAPI(
    title="OSINTGraph API",
    version="0.2.0",
    lifespan=lifespan,
)

origins = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(AuthMiddleware)

app.state.sio = sio

app.include_router(graph.router, prefix="/graph", tags=["graph"])
app.include_router(transforms.router, prefix="/transforms", tags=["transforms"])
app.include_router(workspaces.router, prefix="/workspaces", tags=["workspaces"])
app.include_router(api_v1_router, prefix="/api/v1", tags=["api-v1"])


@app.get("/health")
async def health():
    return {"status": "ok", "service": "OSINTGraph", "version": "0.2.0"}


@sio.event
async def connect(sid, environ):
    logger.info("WebSocket client connected: %s", sid)


@sio.event
async def disconnect(sid):
    logger.info("WebSocket client disconnected: %s", sid)


asgi_app = socketio.ASGIApp(sio, other_asgi_app=app)
