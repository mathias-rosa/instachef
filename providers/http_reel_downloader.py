"""HTTP client wrapper for the reels downloader microservice."""

import asyncio
import json

import httpx

from domain.exceptions import InvalidSourceError, SourceDownloadError, SourceFetchError
from domain.reel import DownloadedReel
from logger import logger


class HttpReelDownloader:
    """HTTP client that calls the downloader microservice."""

    def __init__(
        self,
        base_url: str = "http://reels-downloader:8001",
        timeout: float = 300.0,
        max_retries: int = 3,
    ):
        """
        Initialize HTTP downloader client.

        Args:
            base_url: Base URL of the downloader service (e.g., http://localhost:8001)
            timeout: Request timeout in seconds (default 5 min for large videos)
            max_retries: Number of retry attempts on transient errors
        """
        self.base_url = base_url
        self.timeout = timeout
        self.max_retries = max_retries

    def download_reel(self, reel_url: str) -> DownloadedReel:
        """
        Download a reel by calling the HTTP downloader service.

        Args:
            reel_url: Instagram reel URL

        Returns:
            DownloadedReel with video_path, caption, shortcode, author

        Raises:
            InvalidSourceError: For invalid URLs (HTTP 400)
            SourceDownloadError: For download failures (HTTP 500)
            SourceFetchError: For network/connection errors
        """
        # Use asyncio to run the async HTTP call
        return asyncio.run(self._download_reel_async(reel_url))

    async def _download_reel_async(self, reel_url: str) -> DownloadedReel:
        """Async implementation of download_reel."""
        payload = {"reel_url": reel_url}
        last_error: Exception | None = None

        for attempt in range(1, self.max_retries + 1):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.post(
                        f"{self.base_url}/download",
                        json=payload,
                    )

                if response.status_code == 400:
                    error_detail = response.json().get("detail", "Invalid reel URL")
                    logger.error(f"Invalid source: {error_detail}")
                    raise InvalidSourceError(error_detail)

                if response.status_code == 500:
                    error_detail = response.json().get("detail", "Download failed")
                    logger.error(f"Download service error: {error_detail}")
                    raise SourceDownloadError(error_detail)

                if response.status_code != 200:
                    logger.error(
                        f"Unexpected status {response.status_code}: {response.text}"
                    )
                    raise SourceDownloadError(
                        f"Downloader service returned {response.status_code}"
                    )

                data = response.json()
                result = DownloadedReel(**data)
                logger.info(f"Successfully downloaded reel: {result.shortcode}")
                return result

            except (InvalidSourceError, SourceDownloadError):
                # Don't retry on client errors (400, 500)
                raise
            except httpx.TimeoutException as e:
                last_error = e
                logger.warning(f"Timeout on attempt {attempt}/{self.max_retries}: {e}")
                if attempt < self.max_retries:
                    await asyncio.sleep(2 ** (attempt - 1))  # Exponential backoff
                continue
            except httpx.ConnectError as e:
                last_error = e
                logger.warning(
                    f"Connection error on attempt {attempt}/{self.max_retries}: {e}"
                )
                if attempt < self.max_retries:
                    await asyncio.sleep(2 ** (attempt - 1))  # Exponential backoff
                continue
            except httpx.RequestError as e:
                last_error = e
                logger.warning(
                    f"Request error on attempt {attempt}/{self.max_retries}: {e}"
                )
                if attempt < self.max_retries:
                    await asyncio.sleep(2 ** (attempt - 1))  # Exponential backoff
                continue
            except json.JSONDecodeError as e:
                last_error = e
                logger.error(f"Invalid JSON response from downloader: {e}")
                raise SourceDownloadError("Downloader returned invalid response") from e
            except Exception as e:
                last_error = e
                logger.error(f"Unexpected error during download: {e}", exc_info=True)
                raise SourceFetchError(f"Unexpected error: {e}") from e

        # All retries exhausted
        logger.error(
            f"Failed to download after {self.max_retries} attempts: {last_error}"
        )
        raise SourceFetchError(
            f"Download failed after {self.max_retries} retries"
        ) from last_error
