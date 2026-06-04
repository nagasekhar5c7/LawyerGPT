import logging
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from server.app.config import settings
from server.app.data.database import init_db
from server.app.exceptions import LawyerGPTError
from server.app.exceptions.handlers import lawyergpt_exception_handler, generic_exception_handler
from server.app.routes import conversations, chat, documents


def setup_logging() -> None:
    log_format = "%(asctime)s | %(levelname)-7s | %(name)s | %(message)s"
    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
        format=log_format,
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[logging.StreamHandler(sys.stdout)],
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    logger = logging.getLogger("lawyergpt.main")
    logger.info("Starting LawyerGPT server (env=%s)", settings.APP_ENV)
    await init_db()
    logger.info("Database initialized")
    yield
    logger.info("Shutting down LawyerGPT server")


app = FastAPI(
    title="LawyerGPT API",
    version="0.1.0",
    description="RAG-based legal chatbot API",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(LawyerGPTError, lawyergpt_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

app.include_router(conversations.router)
app.include_router(chat.router)
app.include_router(documents.router)


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "LawyerGPT"}
