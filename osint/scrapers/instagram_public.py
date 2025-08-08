from __future__ import annotations

from typing import List, Dict, Any
from pathlib import Path
import instaloader
from ..utils import ensure_dir, get_logger


logger = get_logger("scrapers.instagram")


def fetch_public_profile(username: str, output_dir: str) -> Dict[str, Any]:
    """Download public profile pictures and posts to output_dir/username. Returns metadata."""
    out = ensure_dir(Path(output_dir) / username)
    L = instaloader.Instaloader(dirname_pattern=str(out), download_comments=False, save_metadata=False, post_metadata_txt_pattern="")
    profile_meta: Dict[str, Any] = {"username": username, "downloaded": False, "path": str(out)}
    try:
        profile = instaloader.Profile.from_username(L.context, username)
        # Download profile pic
        try:
            L.download_profilepic(profile)
        except Exception:
            pass
        # Download recent posts (limit small to be gentle)
        count = 0
        for post in profile.get_posts():
            if count >= 12:
                break
            L.download_post(post, target=profile.username)
            count += 1
        profile_meta["downloaded"] = True
    except Exception as e:
        logger.warning("Failed to fetch Instagram profile %s: %s", username, e)
    return profile_meta