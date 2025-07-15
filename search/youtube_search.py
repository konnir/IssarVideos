#!/usr/bin/env python3
"""
YouTube Search using yt-dlp
A simple class to search for videos on YouTube using yt-dlp
"""

import yt_dlp
from typing import List, Dict, Any, Optional
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
        max_duration: int = 180,
        min_duration: int = 30,
        narrative: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Search for videos on YouTube

        Args:
            query (str): Search query
            max_results (int): Maximum number of results to return
            max_duration (int): Maximum video duration in seconds
            min_duration (int): Minimum video duration in seconds
            narrative (str, optional): Narrative to rank videos by relevance

        Returns:
            List[Dict]: List of video information dictionaries, sorted by narrative relevance if provided
        """
        # Fetch more results to increase the chance of finding videos with the right duration
        # Minimum of 15 videos, or max_results * 5 if user asks for more than 15
        search_count = max(15, max_results * 5)
        rank_count = max_results * 3
        search_query = f"ytsearch{search_count}:{query}"

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
                            and entry.get("view_count", 0) >= 300
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
                            # Don't break early - collect up to rank_count videos for ranking
                            if len(videos) >= rank_count:
                                break

                # If narrative is provided, rank videos by relevance
                if narrative and videos:
                    try:
                        from llm.rank_videos import VideoRanker

                        ranker = VideoRanker()
                        videos = ranker.rank_videos(videos, narrative)
                    except Exception as e:
                        print(
                            f"Warning: Could not rank videos by narrative relevance: {e}"
                        )

                # Return only the top max_results after ranking
                return videos[:max_results]

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

            # Show relevance score if available
            if "relevance_score" in video:
                print(f"   📊 Relevance Score: {video['relevance_score']:.1f}/10")

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

            # Show relevance reasoning if available
            if "relevance_reasoning" in video:
                print(f"   🔍 Relevance: {video['relevance_reasoning']}")

            print("-" * 80)
