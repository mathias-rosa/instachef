from typing import cast
from instaloader import Instaloader, Post


instaloader_instance = Instaloader()


def main():
    reel_url = input("Enter the Instagram Reel URL: ")
    shortcode = reel_url.split("/")[-2]  # Extract shortcode from URL
    try:
        reel: Post = Post.from_shortcode(instaloader_instance.context, shortcode)
        assert isinstance(reel, Post), "The fetched object is not a Post instance."
        reel = cast(Post, reel)  # Cast to Post for type checking
    except Exception as e:
        print(f"Error fetching reel: {e}")
        return

    if not reel.is_video:
        print("The provided URL does not point to a video reel.")
        return

    instaloader_instance.download_post(reel, target="downloaded_reels")

    print(f"Reel URL: {reel_url}")
    print(f"Reel Metadata: {reel._full_metadata}")
    print(f"Reel Caption: {reel.caption}")
    print(f"Reel Video URL: {reel.video_url}")


if __name__ == "__main__":
    main()
