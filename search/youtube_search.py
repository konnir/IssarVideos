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
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True,  # Don't download, just extract metadata
            'default_search': 'ytsearch',  # Use YouTube search
        }
    
    def search_videos(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Search for videos on YouTube
        
        Args:
            query (str): Search query
            max_results (int): Maximum number of results to return
            
        Returns:
            List[Dict]: List of video information dictionaries
        """
        search_query = f"ytsearch{max_results}:{query}"
        
        try:
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                # Extract info without downloading
                search_results = ydl.extract_info(search_query, download=False)
                
                videos = []
                if 'entries' in search_results:
                    for entry in search_results['entries']:
                        if entry:  # Sometimes entries can be None
                            video_info = {
                                'title': entry.get('title', 'Unknown Title'),
                                'url': entry.get('url', ''),
                                'id': entry.get('id', ''),
                                'uploader': entry.get('uploader', 'Unknown'),
                                'duration': entry.get('duration', 0),
                                'view_count': entry.get('view_count', 0),
                                'description': entry.get('description', '')[:200] + '...' if entry.get('description') else ''
                            }
                            videos.append(video_info)
                
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
            duration = video['duration']
            if duration:
                minutes = int(duration) // 60
                seconds = int(duration) % 60
                print(f"   ⏱️  Duration: {minutes}:{seconds:02d}")
            
            # Format view count
            views = video['view_count']
            if views:
                if views >= 1000000:
                    print(f"   👁️  Views: {views/1000000:.1f}M")
                elif views >= 1000:
                    print(f"   👁️  Views: {views/1000:.1f}K")
                else:
                    print(f"   👁️  Views: {views}")
            
            # Show description preview
            if video['description']:
                print(f"   📝 Description: {video['description']}")
            
            print("-" * 80)


if __name__ == "__main__":
    # Create searcher instance
    searcher = YouTubeSearcher()
    
    # Search for "positive body image" videos
    search_query = "positive body image"
    print(f"🔍 Searching YouTube for: '{search_query}'")
    
    # Search for videos
    videos = searcher.search_videos(search_query, max_results=8)
    
    # Print results
    searcher.print_results(videos)
    
    # Also save results to JSON file for later use
    if videos:
        output_file = "positive_body_image_videos.json"
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(videos, f, indent=2, ensure_ascii=False)
            print(f"\n💾 Results saved to: {output_file}")
        except Exception as e:
            print(f"❌ Error saving results: {e}")
