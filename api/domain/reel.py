from pydantic import BaseModel, Field


class DownloadedReel(BaseModel):
    video_path: str = Field(description="Local path to the downloaded video file")
    caption: str = Field(description="Video caption text")
    shortcode: str = Field(description="Unique identifier for the source reel")
    author: str = Field(description="Creator/author name")

    model_config = {"frozen": True}
