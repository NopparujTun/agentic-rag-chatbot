"""Main application entry point for Enterprise Smart KB API."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from dotenv import load_dotenv

from app.api.router import api_router
from app.core.config import load_config

load_dotenv()
logger = logging.getLogger(__name__)

app_config = load_config()

@asynccontextmanager
async def lifespan(fastapi_app: FastAPI):
    """Lifespan events for FastAPI."""
    logger.info("Application starting up... Models will be lazy-loaded on first request.")
    yield
    logger.info("Application shutting down...")


app = FastAPI(title="Enterprise Smart KB API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
