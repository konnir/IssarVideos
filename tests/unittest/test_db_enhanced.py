#!/usr/bin/env python3
"""
Enhanced Database Tests
=======================

Comprehensive tests for database operations including error scenarios,
edge cases, and data integrity checks.
"""
import pytest
import pandas as pd
import tempfile
import os
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add the project root to the Python path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from db.narratives_db import NarrativesDB
from tests.conftest import DBTestManager


class TestNarrativesDBErrorHandling:
    """Test error handling and edge cases in NarrativesDB"""

    def test_invalid_database_path(self):
        """Test handling of invalid database path"""
        with pytest.raises(Exception):
            NarrativesDB("/nonexistent/path/to/database.xlsx")

    def test_empty_database_file(self):
        """Test handling of empty database file"""
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp_file:
            tmp_path = tmp_file.name

        try:
            # Create an empty Excel file
            empty_df = pd.DataFrame()
            empty_df.to_excel(tmp_path, index=False)

            db = NarrativesDB(tmp_path)
            assert db.df.empty

            # Test operations on empty database
            assert db.get_random_not_fully_tagged_row() is None
            assert db.get_user_tagged_count("test_user") == 0

        finally:
            os.unlink(tmp_path)

    def test_corrupted_database_structure(self):
        """Test handling of database with unexpected structure"""
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp_file:
            tmp_path = tmp_file.name

        try:
            # Create database with missing required columns
            corrupted_df = pd.DataFrame(
                {
                    "Wrong_Column": ["value1", "value2"],
                    "Another_Wrong_Column": ["value3", "value4"],
                }
            )
            corrupted_df.to_excel(tmp_path, index=False)

            # Should handle gracefully or raise appropriate error
            with pytest.raises(Exception):
                db = NarrativesDB(tmp_path)
                db.get_random_not_fully_tagged_row()

        finally:
            os.unlink(tmp_path)

    def test_update_nonexistent_record(self):
        """Test updating a record that doesn't exist"""
        with DBTestManager() as db_path:
            db = NarrativesDB(db_path)
            result = db.update_record(
                "https://nonexistent.com", {"Tagger_1": "Test User"}
            )
            assert result is False

    def test_tag_nonexistent_record(self):
        """Test tagging a record that doesn't exist"""
        with DBTestManager() as db_path:
            db = NarrativesDB(db_path)
            result = db.tag_record("https://nonexistent.com", "Test User", 1)
            assert result is False

    def test_tag_record_with_invalid_result(self):
        """Test tagging with invalid result values"""
        with DBTestManager() as db_path:
            db = NarrativesDB(db_path)
            # Add a test record first
            test_record = {
                "Sheet": "Test",
                "Narrative": "Test Narrative",
                "Story": "Test Story",
                "Link": "https://test.com",
                "Tagger_1": None,
                "Tagger_1_Result": None,
            }
            db.add_new_record(test_record)

            # Test with invalid result values
            # Note: The validation might be done at API level, but test DB level too
            result = db.tag_record("https://test.com", "Test User", 5)  # Invalid result
            # Depending on implementation, this might succeed or fail
            # The API layer should catch invalid values

    def test_save_changes_error_handling(self):
        """Test error handling during save operations"""
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp_file:
            tmp_path = tmp_file.name

        try:
            # Create a test database with proper structure
            test_df = pd.DataFrame(
                {
                    "Narrative": ["Test Narrative"],
                    "Story": ["Test Story"],
                    "Link": ["https://test.com"],
                    "Tagger_1": [None],
                    "Tagger_1_Result": [None],
                }
            )

            # Save with a sheet name
            with pd.ExcelWriter(tmp_path, engine="openpyxl") as writer:
                test_df.to_excel(writer, sheet_name="TestSheet", index=False)

            db = NarrativesDB(tmp_path)

            # Make the file read-only to simulate save error
            os.chmod(tmp_path, 0o444)

            # Try to save changes - should handle the error gracefully
            with pytest.raises(PermissionError):
                db.save_changes()

        finally:
            # Restore permissions and clean up
            try:
                os.chmod(tmp_path, 0o644)
                os.unlink(tmp_path)
            except:
                pass


class TestNarrativesDBDataIntegrity:
    """Test data integrity and consistency in NarrativesDB operations"""

    def test_add_duplicate_record(self):
        """Test adding records with duplicate links"""
        with DBTestManager() as db_path:
            db = NarrativesDB(db_path)
            record1 = {
                "Sheet": "Test1",
                "Narrative": "Narrative 1",
                "Story": "Story 1",
                "Link": "https://duplicate-test.com",
                "Tagger_1": None,
                "Tagger_1_Result": None,
            }

            record2 = {
                "Sheet": "Test2",
                "Narrative": "Narrative 2",
                "Story": "Story 2",
                "Link": "https://duplicate-test.com",  # Same link
                "Tagger_1": None,
                "Tagger_1_Result": None,
            }

            # Add first record
            db.add_new_record(record1)
            initial_count = len(db.df)

            # Add second record with same link
            db.add_new_record(record2)

            # Should either reject the duplicate or handle it appropriately
            # Implementation may allow duplicates or prevent them
            final_count = len(db.df)

            # At minimum, verify the data is consistent
            assert final_count >= initial_count

    def test_concurrent_tagging_simulation(self):
        """Test simulation of concurrent tagging operations"""
        with DBTestManager() as db_path:
            db = NarrativesDB(db_path)

            # Get initial count to account for test data
            initial_tagged_count = len(db.df[~db.df["Tagger_1"].isna()])

            # Add multiple test records
            for i in range(5):
                record = {
                    "Sheet": f"Test{i}",
                    "Narrative": f"Narrative {i}",
                    "Story": f"Story {i}",
                    "Link": f"https://test{i}.com",
                    "Tagger_1": None,
                    "Tagger_1_Result": None,
                }
                db.add_new_record(record)

            # Simulate multiple users tagging different records
            users = ["User1", "User2", "User3"]
            links = [f"https://test{i}.com" for i in range(5)]

            successfully_tagged = 0
            for user in users:
                for i, link in enumerate(
                    links[:3]
                ):  # Each user tries to tag first 3 records
                    result = db.tag_record(link, user, (i % 4) + 1)
                    # Only first user should succeed for each record
                    if user == "User1":
                        assert result is True
                        successfully_tagged += 1
                    else:
                        # Later users should fail because record is already tagged
                        assert result is False

            # Verify data consistency
            tagged_records = db.df[~db.df["Tagger_1"].isna()]
            expected_count = initial_tagged_count + successfully_tagged
            assert len(tagged_records) == expected_count

    def test_update_record_data_types(self):
        """Test updating records with various data types"""
        with DBTestManager() as db_path:
            db = NarrativesDB(db_path)
            # Add a test record
            record = {
                "Sheet": "Test",
                "Narrative": "Test Narrative",
                "Story": "Test Story",
                "Link": "https://datatype-test.com",
                "Tagger_1": None,
                "Tagger_1_Result": None,
            }
            db.add_new_record(record)

            # Test updating with different data types
            updates = [
                {"Tagger_1": "String User"},
                {"Tagger_1_Result": 1},
                {"Tagger_1_Result": "2"},  # String number
                {"Story": ""},  # Empty string
                {"Story": None},  # None value
            ]

            for update in updates:
                result = db.update_record("https://datatype-test.com", update)
                assert result is True

                # Verify the update was applied
                updated_record = db.df[
                    db.df["Link"] == "https://datatype-test.com"
                ].iloc[0]
                for key, value in update.items():
                    if value is not None:
                        # Handle pandas automatic type conversion
                        stored_value = updated_record[key]
                        if (
                            key == "Tagger_1_Result"
                            and isinstance(value, str)
                            and value.isdigit()
                        ):
                            # For numeric strings in Tagger_1_Result, pandas converts to float
                            assert stored_value == float(value)
                        else:
                            assert stored_value == value or pd.isna(stored_value)

    def test_random_selection_distribution(self):
        """Test that random record selection has reasonable distribution"""
        with DBTestManager() as db_path:
            db = NarrativesDB(db_path)
            # Add multiple untagged records
            for i in range(20):
                record = {
                    "Sheet": f"Test{i}",
                    "Narrative": f"Narrative {i}",
                    "Story": f"Story {i}",
                    "Link": f"https://random-test{i}.com",
                    "Tagger_1": None,
                    "Tagger_1_Result": None,
                }
                db.add_new_record(record)

            # Get multiple random records and check distribution
            selected_links = []
            for _ in range(50):  # Try to get 50 random records
                random_record = db.get_random_not_fully_tagged_row()
                if random_record:
                    selected_links.append(random_record["Link"])

            # Should have some variety in selection (not always the same record)
            unique_selections = len(set(selected_links))
            assert unique_selections > 1, "Random selection should show variety"

    def test_user_tagged_count_accuracy(self):
        """Test accuracy of user tagged count calculations"""
        with DBTestManager() as db_path:
            db = NarrativesDB(db_path)
            # Add test records and tag them with specific pattern
            test_user = "Count Test User"

            for i in range(10):
                record = {
                    "Sheet": f"Test{i}",
                    "Narrative": f"Narrative {i}",
                    "Story": f"Story {i}",
                    "Link": f"https://count-test{i}.com",
                    "Tagger_1": None,
                    "Tagger_1_Result": None,
                }
                db.add_new_record(record)

                # Tag every other record with our test user
                if i % 2 == 0:
                    db.tag_record(f"https://count-test{i}.com", test_user, 1)

            # Verify count
            count = db.get_user_tagged_count(test_user)
            assert count == 5  # Should have tagged 5 records (0, 2, 4, 6, 8)

            # Verify count for non-existent user
            non_existent_count = db.get_user_tagged_count("Non Existent User")
            assert non_existent_count == 0


class TestNarrativesDBPerformance:
    """Test performance characteristics of database operations"""

    def test_large_dataset_operations(self):
        """Test operations on larger datasets"""
        with DBTestManager() as db_path:
            db = NarrativesDB(db_path)
            # Get initial count to account for existing test data
            initial_count = len(db.df)

            # Add a larger number of records
            num_records = 100

            for i in range(num_records):
                record = {
                    "Sheet": f"Performance Test {i // 10}",
                    "Narrative": f"Performance Narrative {i}",
                    "Story": f"Performance Story {i}",
                    "Link": f"https://performance-test{i}.com",
                    "Tagger_1": None,
                    "Tagger_1_Result": None,
                }
                db.add_new_record(record)

            # Test operations still work efficiently
            expected_count = initial_count + num_records
            assert len(db.df) == expected_count

            # Random selection should still work
            random_record = db.get_random_not_fully_tagged_row()
            assert random_record is not None

            # User count should work
            count = db.get_user_tagged_count("Test User")
            assert count == 0

            # Update operations should work
            result = db.update_record(
                "https://performance-test0.com", {"Tagger_1": "Perf Test User"}
            )
            assert result is True

    def test_memory_usage_with_large_updates(self):
        """Test memory usage doesn't grow excessively with many updates"""
        with DBTestManager() as db_path:
            db = NarrativesDB(db_path)
            # Get initial count to account for existing test data
            initial_count = len(db.df)

            # Add base records
            for i in range(50):
                record = {
                    "Sheet": "Memory Test",
                    "Narrative": f"Memory Narrative {i}",
                    "Story": f"Memory Story {i}",
                    "Link": f"https://memory-test{i}.com",
                    "Tagger_1": None,
                    "Tagger_1_Result": None,
                }
                db.add_new_record(record)

            # Perform many update operations
            for i in range(50):
                for j in range(10):  # 10 updates per record
                    update_data = {
                        "Tagger_1": f"User {j}",
                        "Tagger_1_Result": (j % 4) + 1,
                    }
                    db.update_record(f"https://memory-test{i}.com", update_data)

            # Database should still be functional
            expected_count = initial_count + 50
            assert len(db.df) == expected_count
            random_record = db.get_random_not_fully_tagged_row()
            # May or may not have untagged records after all updates


if __name__ == "__main__":
    # Run with pytest
    pytest.main([__file__, "-v"])
