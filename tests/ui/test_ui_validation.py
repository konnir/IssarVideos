#!/usr/bin/env python3
"""
UI Tests for Video Narratives Project
=====================================

Simple validation tests for HTML files and UI components.
"""
import pytest
from pathlib import Path
import re


class TestUIFiles:
    """Test UI files for basic validity"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup for tests"""
        self.project_root = Path(__file__).parent.parent.parent
        self.static_dir = self.project_root / "static"
        self.ui_test_dir = Path(__file__).parent.parent / "ui"

    def test_main_html_files_exist(self):
        """Test that main HTML files exist and are not empty"""
        required_files = [
            self.static_dir / "tagger.html",
            self.static_dir / "report.html",
        ]

        for file_path in required_files:
            assert file_path.exists(), f"Required file {file_path.name} should exist"
            assert (
                file_path.stat().st_size > 0
            ), f"File {file_path.name} should not be empty"

            # Basic HTML validation
            content = file_path.read_text(encoding="utf-8")
            assert (
                "<!DOCTYPE html>" in content or "<html" in content
            ), f"{file_path.name} should be valid HTML"

    def test_css_files_exist(self):
        """Test that CSS files exist and are not empty"""
        css_files = [
            self.static_dir / "tagger.css",
            self.static_dir / "report.css",
        ]

        for file_path in css_files:
            assert file_path.exists(), f"CSS file {file_path.name} should exist"
            assert (
                file_path.stat().st_size > 0
            ), f"CSS file {file_path.name} should not be empty"

    def test_static_file_content_consistency(self):
        """Test that static files have consistent branding and titles"""
        # Check CSS files for any hardcoded titles or branding
        css_files = [
            self.static_dir / "tagger.css",
            self.static_dir / "report.css",
        ]

        for css_file in css_files:
            if css_file.exists():
                content = css_file.read_text(encoding="utf-8")
                # CSS files should not contain outdated references
                assert (
                    "Video Narratives" not in content or "Narrative Video" in content
                ), f"CSS file {css_file.name} should have consistent branding"

    def test_js_files_exist(self):
        """Test that JavaScript files exist and are not empty"""
        js_files = [
            self.static_dir / "tagger.js",
            self.static_dir / "report.js",
        ]

        for file_path in js_files:
            assert file_path.exists(), f"JS file {file_path.name} should exist"
            assert (
                file_path.stat().st_size > 0
            ), f"JS file {file_path.name} should not be empty"

    def test_tagger_html_structure(self):
        """Test that tagger.html has required elements"""
        tagger_file = self.static_dir / "tagger.html"
        content = tagger_file.read_text(encoding="utf-8")

        # Check for essential elements
        assert 'id="username"' in content, "Should have username input"
        assert 'id="videoContainer"' in content, "Should have video container"
        assert 'id="narrativeEnglish"' in content, "Should have narrative display"
        assert 'name="result"' in content, "Should have result radio buttons"

        # Check that old "Init" option is removed
        assert "0 - Init" not in content, "Should not have Init option"
        assert "1 - Yes" in content, "Should have Yes option"

    def test_tagger_html_title_and_content(self):
        """Test that tagger.html has correct title and main content"""
        tagger_file = self.static_dir / "tagger.html"
        content = tagger_file.read_text(encoding="utf-8")

        # Check page title
        assert (
            "<title>Narrative Video Tagger</title>" in content
        ), "Should have correct page title"

        # Check main heading
        assert (
            "<h1>Narrative Video Tagger</h1>" in content
        ), "Should have correct main heading"

        # Check for leaderboard section
        assert "🏆 Leaderboard" in content, "Should have leaderboard section"
        assert (
            'id="leaderboardSection"' in content
        ), "Should have leaderboard section ID"

        # Check for username section content
        assert "Enter Your Full Name:" in content, "Should have username label"
        assert "Start Tagging" in content, "Should have start tagging button"

    def test_report_html_structure(self):
        """Test that report.html has required elements"""
        report_file = self.static_dir / "report.html"
        content = report_file.read_text(encoding="utf-8")

        # Check for essential elements
        assert 'id="authUsername"' in content, "Should have auth username input"
        assert 'id="authPassword"' in content, "Should have auth password input"
        assert 'id="tableContainer"' in content, "Should have table container"

    def test_report_html_title_and_content(self):
        """Test that report.html has correct title and main content"""
        report_file = self.static_dir / "report.html"
        content = report_file.read_text(encoding="utf-8")

        # Check page title
        assert (
            "<title>Tagger Record Report</title>" in content
        ), "Should have correct page title"

        # Check main heading
        assert "📊 Tagger Record Report" in content, "Should have correct main heading"

        # Check for authentication section
        assert (
            "Authentication Required" in content
        ), "Should have authentication section"
        assert (
            "Please enter your credentials to access the report." in content
        ), "Should have auth instructions"

        # Check for back link
        assert "← Back to Tagger" in content, "Should have back link to tagger"
        assert 'href="/"' in content, "Should have link to homepage"

    def test_ui_test_files_valid(self):
        """Test that UI test files are valid HTML"""
        if not self.ui_test_dir.exists():
            pytest.skip("No UI test directory found")

        html_files = list(self.ui_test_dir.glob("*.html"))
        if not html_files:
            pytest.skip("No HTML test files found")

        for html_file in html_files:
            assert (
                html_file.stat().st_size > 0
            ), f"UI test file {html_file.name} should not be empty"

            content = html_file.read_text(encoding="utf-8")
            assert (
                "html" in content.lower()
            ), f"UI test file {html_file.name} should contain HTML"

    def test_html_accessibility_and_meta(self):
        """Test HTML files for accessibility and proper meta information"""
        html_files = [
            self.static_dir / "tagger.html",
            self.static_dir / "report.html",
        ]

        for html_file in html_files:
            content = html_file.read_text(encoding="utf-8")

            # Check for proper meta tags
            assert (
                'charset="UTF-8"' in content
            ), f"{html_file.name} should have UTF-8 charset"
            assert (
                'name="viewport"' in content
            ), f"{html_file.name} should have viewport meta tag"
            assert (
                'lang="en"' in content
            ), f"{html_file.name} should have language attribute"

            # Check for proper semantic HTML
            assert "<h1>" in content, f"{html_file.name} should have main heading"

            # Check for form accessibility (labels or placeholders)
            if "<input" in content:
                has_labels = "<label" in content
                has_placeholders = "placeholder=" in content
                assert (
                    has_labels or has_placeholders
                ), f"{html_file.name} should have form labels or placeholders for accessibility"


if __name__ == "__main__":
    # Run with pytest
    pytest.main([__file__, "-v"])
