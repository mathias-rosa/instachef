import glob
from typing import cast
from instaloader import Instaloader, Post


class InstagramClient:
    def __init__(self, target_dir: str = "downloaded_reels"):
        self.loader = Instaloader()
        self.target_dir = target_dir

    def download_reel(self, reel_url: str) -> tuple[str, str, str] | None:
        shortcode = reel_url.split("/")[-2]

        try:
            reel: Post = Post.from_shortcode(self.loader.context, shortcode)
            assert isinstance(reel, Post), "The fetched object is not a Post instance."
            reel = cast(Post, reel)
        except Exception as e:
            print(f"Error fetching reel: {e}")
            return None

        if not reel.is_video:
            print("The provided URL does not point to a video reel.")
            return None

        print("Downloading reel (video and caption)...")
        self.loader.download_post(reel, target=self.target_dir)
        print(f"Reel downloaded successfully. Shortcode: {shortcode}")

        video_path = self._find_video_file(shortcode)
        if not video_path:
            return None

        caption = reel.caption or ""
        return video_path, caption, shortcode

    def _find_video_file(self, shortcode: str) -> str | None:
        mp4_files = (
            glob.glob(f"{self.target_dir}/*{shortcode}*.mp4")
            or glob.glob(f"{self.target_dir}/*.mp4")
        )

        if not mp4_files:
            print("Could not find downloaded video.")
            return None

        return mp4_files[0]
