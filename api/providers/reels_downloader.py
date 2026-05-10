from glob import glob
from pathlib import Path

from instaloader import Instaloader, Post

from domain.exceptions import InvalidSourceError, SourceDownloadError, SourceFetchError
from domain.reel import DownloadedReel
from logger import logger


class ReelDownloader:
    def __init__(self, target_dir: str = "downloaded_reels"):
        self.target_dir = target_dir

    def download_reel(self, reel_url: str) -> DownloadedReel:
        shortcode = self._extract_shortcode(reel_url)
        if not shortcode:
            logger.error("Invalid source URL provided for reel download.")
            raise InvalidSourceError(
                "The provided URL does not appear to be a valid Instagram Reel URL."
            )

        loader = Instaloader(filename_pattern="{shortcode}")

        try:
            reel = self._fetch_post(loader, shortcode)
        except Exception as e:
            logger.error(f"Error fetching reel: {e}")
            raise SourceFetchError(f"Error fetching reel: {e}") from e

        if not reel.is_video:
            logger.error("The provided URL does not point to a video reel.")
            raise InvalidSourceError("The provided URL does not point to a video reel.")

        logger.info("Downloading reel (video and caption)...")
        try:
            loader.download_post(reel, target=self.target_dir)
        except Exception as e:
            logger.error(f"Error downloading reel media: {e}")
            raise SourceDownloadError(f"Error downloading reel media: {e}") from e
        logger.info(f"Reel downloaded successfully. Shortcode: {shortcode}")

        video_path = self._expected_video_path(reel.shortcode)
        if not video_path or not Path(video_path).exists():
            video_path = self._find_video_file(shortcode)
        if not video_path:
            logger.error("Could not find downloaded video.")
            raise SourceDownloadError("Could not find downloaded video.")

        caption = reel.caption or ""
        return DownloadedReel(
            video_path=video_path,
            caption=caption,
            shortcode=shortcode,
            author=reel.owner_username,
        )

    @staticmethod
    def _extract_shortcode(reel_url: str) -> str | None:
        url_array = reel_url.split("/")
        is_reel = len(url_array) >= 3 and url_array[-3] == "reel"
        if not is_reel:
            return None

        shortcode = url_array[-2]
        if not shortcode:
            return None
        return shortcode

    def _fetch_post(self, loader: Instaloader, shortcode: str) -> Post:
        reel: Post = Post.from_shortcode(loader.context, shortcode)
        assert isinstance(reel, Post), "The fetched object is not a Post instance."
        return reel

    def _expected_video_path(self, shortcode: str) -> str:
        return str(Path(self.target_dir) / f"{shortcode}.mp4")

    def _find_video_file(self, shortcode: str) -> str | None:
        mp4_files = glob(f"{self.target_dir}/{shortcode}*.mp4")
        if not mp4_files:
            return None

        return max(mp4_files, key=lambda p: Path(p).stat().st_mtime)
