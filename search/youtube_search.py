#!/usr/bin/env python3
"""
YouTube Search using yt-dlp
A simple class to search for videos on YouTube using yt-dlp
"""

import yt_dlp
from typing import List, Dict, Any
import json


class YouTubeSearcher:
    """Simple YouTube video searcher using yt-dlp"""

    def __init__(self):
        """Initialize the YouTube searcher with basic yt-dlp options"""
        self.ydl_opts = {
            "quiet": True,
            "no_warnings": True,
            "extract_flat": True,  # Don't download, just extract metadata
            "default_search": "ytsearch",  # Use YouTube search
        }

    def search_videos(
        self,
        query: str,
        max_results: int = 3,
        max_duration: int = 300,
        min_duration: int = 45,
    ) -> List[Dict[str, Any]]:
        """
        Search for videos on YouTube

        Args:
            query (str): Search query
            max_results (int): Maximum number of results to return
            max_duration (int): Maximum video duration in seconds
            min_duration (int): Minimum video duration in seconds

        Returns:
            List[Dict]: List of video information dictionaries
        """
        # Fetch more results to increase the chance of finding videos with the right duration
        search_query = f"ytsearch{max_results * 5}:{query}"

        try:
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                # Extract info without downloading
                search_results = ydl.extract_info(search_query, download=False)

                videos = []
                if "entries" in search_results:
                    for entry in search_results["entries"]:
                        if (
                            entry
                            and entry.get("duration")
                            and entry["duration"] >= min_duration
                            and entry["duration"] <= max_duration
                        ):
                            video_info = {
                                "title": entry.get("title", "Unknown Title"),
                                "url": entry.get("url", ""),
                                "id": entry.get("id", ""),
                                "uploader": entry.get("uploader", "Unknown"),
                                "duration": entry.get("duration", 0),
                                "view_count": entry.get("view_count", 0),
                                "description": (
                                    entry.get("description", "")[:200] + "..."
                                    if entry.get("description")
                                    else ""
                                ),
                            }
                            videos.append(video_info)
                            if len(videos) == max_results:
                                break

                return videos

        except Exception as e:
            print(f"Error searching for videos: {e}")
            return []

    def print_results(self, videos: List[Dict[str, Any]]) -> None:
        """
        Print search results in a formatted way

        Args:
            videos (List[Dict]): List of video information
        """
        if not videos:
            print("No videos found.")
            return

        print(f"\n🎥 Found {len(videos)} videos:\n")
        print("-" * 80)

        for i, video in enumerate(videos, 1):
            print(f"{i}. {video['title']}")
            print(f"   👤 Uploader: {video['uploader']}")
            print(f"   🔗 URL: https://youtube.com/watch?v={video['id']}")

            # Format duration
            duration = video["duration"]
            if duration:
                minutes = int(duration) // 60
                seconds = int(duration) % 60
                print(f"   ⏱️  Duration: {minutes}:{seconds:02d}")

            # Format view count
            views = video["view_count"]
            if views:
                if views >= 1000000:
                    print(f"   👁️  Views: {views/1000000:.1f}M")
                elif views >= 1000:
                    print(f"   👁️  Views: {views/1000:.1f}K")
                else:
                    print(f"   👁️  Views: {views}")

            # Show description preview
            if video["description"]:
                print(f"   📝 Description: {video['description']}")

            print("-" * 80)
