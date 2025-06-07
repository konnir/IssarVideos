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

    def test_main_html_files_exist(self):
        """Test that main HTML files exist and are not empty"""
        required_files = [
            self.static_dir / "tagger.html",
            self.static_dir / "report.html",
            self.static_dir / "tagging-management.html",
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
            self.static_dir / "tagging-management.css",
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

    def test_tagging_management_page_structure(self):
        """Test that tagging management page has proper structure"""
        tagging_mgmt_file = self.static_dir / "tagging-management.html"
        assert tagging_mgmt_file.exists(), "Tagging management HTML file should exist"

        content = tagging_mgmt_file.read_text(encoding="utf-8")

        # Check for essential elements
        assert "📋 Tagging Management" in content, "Should have page title"
        assert "authSection" in content, "Should have authentication section"
        assert "managementContent" in content, "Should have management content section"
        assert "managementTable" in content, "Should have management table"

        # Check for table columns
        required_columns = [
            "Topic",
            "Narrative",
            "Initial",
            "Yes",
            "No",
            "Too Obvious",
            "Problem",
            "Missing",
        ]
        for column in required_columns:
            assert column in content, f"Should have {column} column in table"

        # Check for JavaScript integration
        assert (
            "tagging-management.js" in content
        ), "Should include tagging management JavaScript"

        # Check for proper CSS links
        assert (
            "tagging-management.css" in content
        ), "Should include tagging management CSS"

        print("✅ Tagging management page structure validation passed")

    def test_add_narrative_modal_structure(self):
        """Test that Add Narrative modal has proper structure and functionality"""
        tagging_mgmt_file = self.static_dir / "tagging-management.html"
        content = tagging_mgmt_file.read_text(encoding="utf-8")

        # Check for Add Narrative button
        assert "Add Narrative" in content, "Should have Add Narrative button"
        assert "add-narrative-btn" in content, "Should have Add Narrative button class"
        assert "showAddNarrativeModal()" in content, "Should have modal show function"

        # Check for modal structure
        assert "addNarrativeModal" in content, "Should have Add Narrative modal"
        assert "modal-content" in content, "Should have modal content structure"
        assert "modal-header" in content, "Should have modal header"
        assert "modal-body" in content, "Should have modal body"
        assert "Add New Narrative" in content, "Should have modal title"

        # Check for form fields
        required_form_fields = [
            'id="sheet1"',  # Topic field
            'id="narrative1"',  # Narrative field
            'id="story1"',  # Story field
            'id="link1"',  # Link field
        ]
        for field in required_form_fields:
            assert field in content, f"Should have form field {field}"

        # Check for form labels
        form_labels = ["Topic:", "Narrative:", "Story:", "Link:", "Actions:"]
        for label in form_labels:
            assert label in content, f"Should have form label {label}"

        # Check for plus button functionality
        assert "plus-btn" in content, "Should have plus button for adding new lines"
        assert "addNewFormLine" in content, "Should have add new line functionality"
        assert "+" in content, "Should have plus button text"

        # Check for button group structure
        assert (
            "button-group" in content
        ), "Should have button group for Add and Plus buttons"
        assert (
            "addSingleNarrative" in content
        ), "Should have add single narrative function"

        # Check for user tip section
        assert "user-tip" in content, "Should have user tip section"
        assert "Tip:" in content, "Should have tip content"
        assert "duplicate links" in content.lower(), "Should warn about duplicate links"

        print("✅ Add Narrative modal structure validation passed")

    def test_add_narrative_form_layout(self):
        """Test that Add Narrative form has proper grid layout and styling"""
        tagging_mgmt_file = self.static_dir / "tagging-management.html"
        content = tagging_mgmt_file.read_text(encoding="utf-8")

        # Check for grid layout CSS
        assert "display: grid" in content, "Should use CSS grid layout"
        assert "grid-template-columns" in content, "Should have grid column definitions"
        assert (
            "0.42fr 1.5fr 3fr 1.5fr auto" in content
        ), "Should have correct grid proportions"

        # Check for gap spacing
        assert "gap: 30px" in content, "Should have 30px gap between form fields"

        # Check for form field grid positioning
        grid_positions = [
            "grid-column: 1",  # Topic
            "grid-column: 2",  # Narrative
            "grid-column: 3",  # Story
            "grid-column: 4",  # Link
            "grid-column: 5",  # Actions
        ]
        for position in grid_positions:
            assert position in content, f"Should have grid position {position}"

        # Check for horizontal layout enforcement
        assert "flex-direction: row" in content, "Should enforce horizontal layout"
        assert "flex-wrap: nowrap" in content, "Should prevent wrapping"

        print("✅ Add Narrative form layout validation passed")

    def test_add_narrative_javascript_integration(self):
        """Test that Add Narrative JavaScript functionality is properly integrated"""
        js_file = self.static_dir / "tagging-management.js"
        assert js_file.exists(), "tagging-management.js should exist"

        content = js_file.read_text(encoding="utf-8")

        # Check for modal functions
        modal_functions = [
            "showAddNarrativeModal",
            "hideAddNarrativeModal",
            "addSingleNarrative",
            "addNewFormLine",
            "createFormLineHTML",
            "resetFormContainer",
        ]
        for func in modal_functions:
            assert func in content, f"Should have {func} function"

        # Check for form line counter
        assert "formLineCounter" in content, "Should have form line counter"

        # Check for field copying logic
        assert "sourceTopic" in content, "Should copy topic field"
        assert "sourceNarrative" in content, "Should copy narrative field"

        # Check for API call to add-narrative endpoint
        assert "/add-narrative" in content, "Should call add-narrative API endpoint"
        assert "POST" in content, "Should use POST method"

        # Check for error handling
        assert "errorDiv" in content, "Should have error handling"
        assert "Added ✓" in content, "Should show success state"

        # Check for duplicate link validation
        assert "link already exists" in content, "Should handle duplicate link errors"

        print("✅ Add Narrative JavaScript integration validation passed")
