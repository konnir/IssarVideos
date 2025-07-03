import unittest
from unittest.mock import patch, MagicMock
from search.youtube_search import YouTubeSearcher
import io


class TestYouTubeSearcher(unittest.TestCase):
    def setUp(self):
        self.searcher = YouTubeSearcher()

    @patch("yt_dlp.YoutubeDL")
    def test_search_videos_success(self, mock_youtube_dl):
        mock_extract_info = MagicMock()
        mock_extract_info.return_value = {
            "entries": [
                {
                    "id": "123",
                    "title": "Test Video 1",
                    "uploader": "Test Uploader",
                    "duration": 180,
                    "view_count": 1000,
                    "description": "Test description",
                    "url": "http://example.com/video1",
                },
                {
                    "id": "456",
                    "title": "Test Video 2",
                    "uploader": "Test Uploader 2",
                    "duration": 400,
                    "view_count": 2000000,
                    "description": "Test description 2",
                    "url": "http://example.com/video2",
                },
            ]
        }
        mock_youtube_dl.return_value.__enter__.return_value.extract_info = (
            mock_extract_info
        )

        videos = self.searcher.search_videos("test query", max_results=1)
        self.assertEqual(len(videos), 1)
        self.assertEqual(videos[0]["title"], "Test Video 1")

        videos = self.searcher.search_videos(
            "test query", max_results=2, max_duration=500
        )
        self.assertEqual(len(videos), 2)

    @patch("yt_dlp.YoutubeDL")
    def test_search_videos_no_results(self, mock_youtube_dl):
        mock_extract_info = MagicMock()
        mock_extract_info.return_value = {"entries": []}
        mock_youtube_dl.return_value.__enter__.return_value.extract_info = (
            mock_extract_info
        )

        videos = self.searcher.search_videos("test query")
        self.assertEqual(len(videos), 0)

    @patch("yt_dlp.YoutubeDL")
    def test_search_videos_exception(self, mock_youtube_dl):
        mock_youtube_dl.side_effect = Exception("Test Exception")
        videos = self.searcher.search_videos("test query")
        self.assertEqual(len(videos), 0)

    @patch("sys.stdout", new_callable=io.StringIO)
    def test_print_results(self, mock_stdout):
        videos = [
            {
                "id": "123",
                "title": "Test Video 1",
                "uploader": "Test Uploader",
                "duration": 180,
                "view_count": 1500,
                "description": "Test description",
            },
            {
                "id": "456",
                "title": "Test Video 2",
                "uploader": "Test Uploader 2",
                "duration": 60,
                "view_count": 1500000,
                "description": "Test description 2",
            },
        ]
        self.searcher.print_results(videos)
        output = mock_stdout.getvalue()
        self.assertIn("Test Video 1", output)
        self.assertIn("1.5K", output)
        self.assertIn("1.5M", output)
        self.assertIn("3:00", output)

    @patch("sys.stdout", new_callable=io.StringIO)
    def test_print_results_no_videos(self, mock_stdout):
        self.searcher.print_results([])
        self.assertIn("No videos found.", mock_stdout.getvalue())


if __name__ == "__main__":
    unittest.main()
