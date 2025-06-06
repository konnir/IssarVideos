#!/usr/bin/env python3
"""
Test configuration and utilities for the Video Narratives API
"""
import os
import shutil
import tempfile
import pytest
from pathlib import Path

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent
ORIGINAL_DB_PATH = PROJECT_ROOT / "static" / "db" / "narratives_db.xlsx"


class DBTestManager:
    """Context manager for handling test database setup and cleanup"""

    def __init__(self):
        self.temp_dir = None
        self.test_db_path = None
        self.original_db_path = ORIGINAL_DB_PATH

        # Safety check: ensure we're not accidentally using production DB
        if not self.original_db_path.exists():
            raise FileNotFoundError(
                f"Production database not found: {self.original_db_path}"
            )

    def __enter__(self):
        # Create temporary directory
        self.temp_dir = tempfile.mkdtemp(prefix="narratives_test_")

        # Copy the original database to temp location
        self.test_db_path = os.path.join(self.temp_dir, "test_narratives_db.xlsx")

        # Create a test database without Tagger_2 columns
        import pandas as pd

        # Create test data with proper structure (without Tagger_2 columns)
        # Create test data with proper structure (without old fields, with empty Tagger_1)
        test_data = [
            {
                "Narrative": "Test narrative for unit testing",
                "Story": "Test story content",
                "Link": "https://youtube.com/test-unit-12345",
                "Tagger_1": None,  # Empty instead of "Init"
                "Tagger_1_Result": None,
            },
            {
                "Narrative": "Second test narrative",
                "Story": "Another test story",
                "Link": "https://youtube.com/test-unit-67890",
                "Tagger_1": "TestUser",
                "Tagger_1_Result": 1,
            },
            {
                "Narrative": "Third test narrative for filtering",
                "Story": None,  # Test empty story
                "Link": "https://youtube.com/test-unit-11111",
                "Tagger_1": None,  # Empty for testing untagged records
                "Tagger_1_Result": None,
            },
        ]

        # Create DataFrame and save to Excel
        df = pd.DataFrame(test_data)
        with pd.ExcelWriter(self.test_db_path, engine="openpyxl") as writer:
            df.to_excel(writer, sheet_name="TestSheet", index=False)

        # Additional safety check: ensure test path contains "test" or "temp"
        if not (
            "test" in self.test_db_path.lower() or "temp" in self.test_db_path.lower()
        ):
            raise ValueError(
                f"Test database path must contain 'test' or 'temp': {self.test_db_path}"
            )

        print(f"📁 Test DB created at: {self.test_db_path}")
        return self.test_db_path

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Clean up temporary directory and files
        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
            print(f"🗑️  Test DB cleaned up: {self.temp_dir}")


def get_test_db_path():
    """Get a temporary copy of the database for testing"""
    return DBTestManager()


def verify_production_db_protection():
    """Verify that no tests are using the production database"""
    import os

    current_db_path = os.getenv("NARRATIVES_DB_PATH")
    if current_db_path:
        if (
            "test" not in current_db_path.lower()
            and "temp" not in current_db_path.lower()
        ):
            raise ValueError(
                f"❌ DANGER: Tests are configured to use production database: {current_db_path}"
            )
        print(f"✅ Tests are safely using test database: {current_db_path}")
    else:
        print("✅ No NARRATIVES_DB_PATH set, using default test isolation")


def get_test_record_data():
    """Return sample test record data"""
    return {
        "Sheet": "TestSheet",
        "Narrative": "Test narrative for unit testing",
        "Story": "Test story content",
        "Link": "https://youtube.com/test-unit-12345",
        "Tagger_1": "TestUser1",
        "Tagger_1_Result": 1,
    }


def get_test_update_data():
    """Return sample update data for testing"""
    return {
        "Tagger_1": "UpdatedUser",
        "Tagger_1_Result": 2,
    }
