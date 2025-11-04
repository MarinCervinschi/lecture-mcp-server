import uvicorn

from app.core.config import settings


def main() -> None:
    """Run the application with configured settings."""

    reload = settings.RELOAD and settings.is_development
    workers = 1 if reload else settings.WORKERS

    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=reload,
        workers=workers,
        log_level=settings.LOG_LEVEL.lower(),
        access_log=settings.is_development,
    )


if __name__ == "__main__":
    main()
