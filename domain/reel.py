from dataclasses import dataclass


@dataclass(frozen=True)
class DownloadedReel:
    video_path: str
    caption: str
    shortcode: str
