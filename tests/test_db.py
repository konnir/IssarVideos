#!/usr/bin/env python3
"""
Unit tests for the NarrativesDB class
"""
import pytest
import pandas as pd
import os
from pathlib import Path
import sys

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from db.narratives_db import NarrativesDB
from tests.conftest import DBTestManager, get_test_record_data, get_test_update_data


class TestNarrativesDB:
    """Test suite for NarrativesDB class"""

    def test_init_and_load_data(self):
        """Test database initialization and data loading"""
        with DBTestManager() as test_db_path:
            db = NarrativesDB(test_db_path)

            # Check that data was loaded
            assert not db.df.empty, "Database should not be empty"
            assert "Sheet" in db.df.columns, "Should have 'Sheet' column"
            assert "Link" in db.df.columns, "Should have 'Link' column"
            assert "Tagger_1" in db.df.columns, "Should have 'Tagger_1' column"
            assert (
                "Tagger_1_Result" in db.df.columns
            ), "Should have 'Tagger_1_Result' column"
            # Tagger_2 columns should not exist anymore
            assert "Tagger_2" not in db.df.columns, "Should not have 'Tagger_2' column"
            assert (
                "Tagger_2_Result" not in db.df.columns
            ), "Should not have 'Tagger_2_Result' column"

            print(f"✅ Loaded {len(db.df)} records from test database")

    def test_get_random_not_fully_tagged_row(self):
        """Test getting random untagged rows"""
        with DBTestManager() as test_db_path:
            db = NarrativesDB(test_db_path)

            # Get a random untagged row
            random_row = db.get_random_not_fully_tagged_row()

            assert random_row is not None, "Should find untagged rows"
            assert isinstance(random_row, dict), "Should return a dictionary"
            assert "Link" in random_row, "Should have Link field"
            assert (
                random_row["Tagger_1"] == "Init"
            ), "Should have 'Init' tagger"

            print(f"✅ Found untagged record: {random_row['Link']}")

    def test_add_new_record(self):
        """Test adding a new record"""
        with DBTestManager() as test_db_path:
            db = NarrativesDB(test_db_path)
            original_count = len(db.df)

            # Add a test record
            test_record = get_test_record_data()
            result = db.add_new_record(test_record)

            assert result is True, "Should successfully add record"
            assert len(db.df) == original_count + 1, "Should increase record count by 1"

            # Check that the record was added correctly
            new_record = db.df[db.df["Link"] == test_record["Link"]].iloc[0]
            assert new_record["Title"] == test_record["Title"], "Title should match"
            assert (
                new_record["Narrative"] == test_record["Narrative"]
            ), "Narrative should match"

            print(f"✅ Successfully added record: {test_record['Link']}")

    def test_update_record(self):
        """Test updating an existing record"""
        with DBTestManager() as test_db_path:
            db = NarrativesDB(test_db_path)

            # First add a record to update
            test_record = get_test_record_data()
            db.add_new_record(test_record)

            # Update the record
            update_data = get_test_update_data()
            result = db.update_record(test_record["Link"], update_data)

            assert result is True, "Should successfully update record"

            # Check that the record was updated
            updated_record = db.df[db.df["Link"] == test_record["Link"]].iloc[0]
            assert (
                updated_record["Tagger_1"] == update_data["Tagger_1"]
            ), "Tagger_1 should be updated"
            assert (
                updated_record["Tagger_1_Result"] == update_data["Tagger_1_Result"]
            ), "Tagger_1_Result should be updated"
            # Tagger_2 fields no longer exist
            assert "Tagger_2" not in updated_record.index, "Tagger_2 should not exist"
            assert "Tagger_2_Result" not in updated_record.index, "Tagger_2_Result should not exist"

            print(f"✅ Successfully updated record: {test_record['Link']}")

    def test_update_nonexistent_record(self):
        """Test updating a record that doesn't exist"""
        with DBTestManager() as test_db_path:
            db = NarrativesDB(test_db_path)

            # Try to update a non-existent record
            fake_link = "https://fake-link-that-does-not-exist.com"
            update_data = get_test_update_data()
            result = db.update_record(fake_link, update_data)

            assert result is False, "Should return False for non-existent record"
            print("✅ Correctly handled non-existent record update")

    def test_save_changes(self):
        """Test saving changes to Excel file"""
        with DBTestManager() as test_db_path:
            db = NarrativesDB(test_db_path)

            # Add a test record
            test_record = get_test_record_data()
            db.add_new_record(test_record)

            # Save changes
            result = db.save_changes()
            assert result is True, "Should successfully save changes"

            # Verify the file was updated by loading it again
            db2 = NarrativesDB(test_db_path)
            saved_record = db2.df[db2.df["Link"] == test_record["Link"]]
            assert not saved_record.empty, "Record should be saved to file"

            print("✅ Successfully saved changes to Excel file")

    def test_get_excel_bytes(self):
        """Test getting Excel file as bytes"""
        with DBTestManager() as test_db_path:
            db = NarrativesDB(test_db_path)

            excel_bytes = db.get_excel_bytes()

            assert isinstance(excel_bytes, bytes), "Should return bytes"
            assert len(excel_bytes) > 0, "Should return non-empty bytes"

            print(f"✅ Generated Excel bytes: {len(excel_bytes)} bytes")


if __name__ == "__main__":
    # Run tests directly if this script is executed
    test_db = TestNarrativesDB()

    print("🧪 Running NarrativesDB Tests...")
    print("=" * 50)

    try:
        test_db.test_init_and_load_data()
        test_db.test_get_random_not_fully_tagged_row()
        test_db.test_add_new_record()
        test_db.test_update_record()
        test_db.test_update_nonexistent_record()
        test_db.test_save_changes()
        test_db.test_get_excel_bytes()

        print("=" * 50)
        print("🎉 All tests passed!")

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
        exit(1)
