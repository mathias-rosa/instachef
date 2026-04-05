import glob
from typing import cast

from instaloader import Instaloader, Post

from logger import logger
from domain.reel import DownloadedReel


class ReelDownloader:
    def __init__(self, target_dir: str = "downloaded_reels"):
        self.loader = Instaloader()
        self.target_dir = target_dir

    def download_reel(self, reel_url: str) -> DownloadedReel | None:
        shortcode = self._extract_shortcode(reel_url)
        if not shortcode:
            logger.warning(
                "The provided URL does not appear to be a valid Instagram Reel URL."
            )
            return None

        try:
            reel = self._fetch_post(shortcode)
        except Exception as e:
            logger.error(f"Error fetching reel: {e}")
            return None

        if not reel.is_video:
            logger.warning("The provided URL does not point to a video reel.")
            return None

        logger.info("Downloading reel (video and caption)...")
        self.loader.download_post(reel, target=self.target_dir)
        logger.info(f"Reel downloaded successfully. Shortcode: {shortcode}")

        video_path = self._find_video_file(shortcode)
        if not video_path:
            return None

        caption = reel.caption or ""
        return DownloadedReel(
            video_path=video_path, caption=caption, shortcode=shortcode
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

    def _fetch_post(self, shortcode: str) -> Post:
        reel: Post = Post.from_shortcode(self.loader.context, shortcode)
        assert isinstance(reel, Post), "The fetched object is not a Post instance."
        return cast(Post, reel)

    def _find_video_file(self, shortcode: str) -> str | None:
        primary_match = glob.glob(f"{self.target_dir}/*{shortcode}*.mp4")
        fallback_match = glob.glob(f"{self.target_dir}/*.mp4")
        mp4_files = primary_match or fallback_match

        if not mp4_files:
            logger.error("Could not find downloaded video.")
            return None

        return mp4_files[0]
