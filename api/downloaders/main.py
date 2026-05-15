"""FastAPI downloader service for Instagram Reels."""

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from domain.exceptions import InvalidSourceError, SourceDownloadError, SourceFetchError
from domain.reel import DownloadedReel
from logger import logger
from providers.reels_downloader import ReelDownloader


class DownloadRequest(BaseModel):
    """Request schema for downloading a reel."""

    reel_url: str = Field(description="Instagram Reel URL to download")


class ErrorResponse(BaseModel):
    """Error response schema."""

    detail: str
    error_code: str


# Initialize the downloader once at startup
downloader: ReelDownloader | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown."""
    global downloader
    # Startup
    downloader = ReelDownloader(target_dir="downloaded_reels")
    logger.info("Downloader service started")
    yield
    # Shutdown
    logger.info("Downloader service shutting down")


app = FastAPI(
    title="Cookachu Reels Downloader",
    description="Microservice for downloading Instagram Reels",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}


@app.post(
    "/download",
    response_model=DownloadedReel,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid reel URL"},
        500: {"model": ErrorResponse, "description": "Download failed"},
    },
)
async def download_reel(request: DownloadRequest) -> DownloadedReel:
    """
    Download a reel and return metadata.

    Args:
        request: DownloadRequest with reel_url

    Returns:
        DownloadedReel with video_path, caption, shortcode, author

    Raises:
        HTTPException: 400 for invalid URL, 500 for download errors
    """
    if not downloader:
        logger.error("Downloader not initialized")
        raise HTTPException(
            status_code=500,
            detail="Downloader service not initialized",
        )

    try:
        logger.info(f"Processing download request for: {request.reel_url}")
        result = downloader.download_reel(request.reel_url)
        logger.info(f"Successfully downloaded reel: {result.shortcode}")
        return result

    except InvalidSourceError as e:
        logger.warning(f"Invalid source error: {e}")
        raise HTTPException(status_code=400, detail=str(e)) from e

    except (SourceFetchError, SourceDownloadError) as e:
        logger.error(f"Download error: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e

    except Exception as e:
        logger.error(f"Unexpected error during download: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail="Unexpected error during download"
        ) from e


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001)
