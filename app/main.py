from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes import evaluation, health, models, search
from app.core.config import settings
from app.core.exceptions import MedicalSearchError
from app.core.logging import logger, setup_logging
from app.services.retrieval_service import RetrievalService


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI Lifespan Context Manager.
    Initializes all retrieval engines, indexes, spaCy models, and embedding caches ONCE at startup.
    Reuses the initialized shared service instance for all incoming requests.
    """
    setup_logging()
    logger.info(f"Starting {settings.PROJECT_NAME} v{settings.VERSION}...")

    retrieval_service = RetrievalService(settings)
    try:
        retrieval_service.initialize()
        app.state.retrieval_service = retrieval_service
        logger.info("Application startup complete. Ready to serve search requests.")
        yield
    except Exception as e:
        logger.critical(f"Application failed to initialize during startup: {str(e)}")
        raise e
    finally:
        logger.info("Shutting down application...")
        if hasattr(app.state, "retrieval_service") and app.state.retrieval_service is not None:
            app.state.retrieval_service.close()


def create_application() -> FastAPI:
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        description="Production-ready FastAPI backend for Medical Search on NFCorpus dataset.",
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
    )

    # Configure CORS
    cors_origins = (
        [settings.CORS_ORIGINS]
        if isinstance(settings.CORS_ORIGINS, str)
        else settings.CORS_ORIGINS
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include API Routes
    v1_router = FastAPI().router
    v1_router.include_router(health.router, tags=["Health"])
    v1_router.include_router(search.router, tags=["Search"])
    v1_router.include_router(models.router, tags=["Models"])
    v1_router.include_router(evaluation.router, tags=["Evaluation"])

    app.include_router(v1_router, prefix=settings.API_V1_STR)

    @app.exception_handler(MedicalSearchError)
    async def medical_search_exception_handler(request: Request, exc: MedicalSearchError):
        return JSONResponse(
            status_code=400,
            content={"detail": str(exc)}
        )

    return app


app = create_application()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
