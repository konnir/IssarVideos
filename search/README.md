# Video Search Module

This module provides YouTube video search functionality using `yt-dlp`.

## Features

- Search for videos on YouTube using natural language queries
- Extract video metadata without downloading videos
- Save search results for later processing
- Pretty-print search results in the terminal

## Usage

### Basic Usage

```python
from search import YouTubeSearcher

# Create a searcher instance
searcher = YouTubeSearcher()

# Search for videos with a specific query
videos = searcher.search_videos("positive body image", max_results=8)

# Print the search results
searcher.print_results(videos)
```

### Command Line Usage

You can also run the module directly:

```bash
python search/youtube_search.py
```

This will search for "positive body image" videos by default and save the results to `search/data/positive_body_image_videos.json`.

## Output

The search results include the following metadata for each video:

- Title
- URL
- Video ID
- Uploader
- Duration
- View count
- Description (truncated)

## Dependencies

This module requires `yt-dlp` which is already included in the project dependencies.
