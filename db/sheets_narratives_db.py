"""
Google Sheets-based database for narratives, replacing Excel operations.
"""

import logging
import pandas as pd
import random
from typing import Optional, Dict, Any, List
from clients.sheets_client import SheetsClient

logger = logging.getLogger(__name__)


class SheetsNarrativesDB:
    """Database operations using Google Sheets instead of Excel files."""

    def __init__(
        self, credentials_path: Optional[str] = None, sheet_id: Optional[str] = None
    ):
        """
        Initialize the Google Sheets database.

        Args:
            credentials_path: Path to service account JSON credentials
            sheet_id: Google Sheets document ID
        """
        self.sheets_client = SheetsClient(credentials_path, sheet_id)
        self.df = pd.DataFrame()
        self.current_sheet_name = None
        self.load_data()

    def load_data(self, sheet_name: str = None):
        """
        Load data from Google Sheets into memory.

        Args:
            sheet_name: Specific sheet to load, or first sheet if None
        """
        try:
            # If no sheet name provided, get the first worksheet
            if not sheet_name:
                worksheets = self.sheets_client.get_all_worksheets()
                if worksheets:
                    sheet_name = worksheets[0]
                else:
                    logger.warning("No worksheets found in the spreadsheet")
                    return

            self.current_sheet_name = sheet_name
            self.df = self.sheets_client.read_sheet_to_dataframe(sheet_name)

            # Update timestamp
            import time

            self.last_loaded_time = time.time()

            logger.info(f"Loaded {len(self.df)} records from Google Sheets")

        except Exception as e:
            logger.error(f"Failed to load data from Google Sheets: {str(e)}")
            # Initialize empty DataFrame with expected columns
            self.df = pd.DataFrame(
                columns=[
                    "Sheet",
                    "Narrative",
                    "Story",
                    "Link",
                    "Tagger_1",
                    "Tagger_1_Result",
                ]
            )

    def save_changes(self):
        """Save the current DataFrame back to Google Sheets."""
        try:
            if self.df.empty:
                logger.warning("No data to save")
                return

            self.sheets_client.write_dataframe_to_sheet(
                self.df, self.current_sheet_name, clear_sheet=True
            )

            logger.info(f"Successfully saved {len(self.df)} records to Google Sheets")

        except Exception as e:
            logger.error(f"Failed to save changes to Google Sheets: {str(e)}")
            raise

    def get_random_not_fully_tagged_row(self) -> Optional[Dict[str, Any]]:
        """Get a random row that is not fully tagged."""
        # No auto-refresh - use cached data only
        # Call /refresh-data endpoint manually to update

        if self.df.empty:
            return None

        # Filter rows where Tagger_1 is empty/null
        untagged_df = self.df[
            (self.df["Tagger_1"].isna()) | (self.df["Tagger_1"] == "")
        ]

        if untagged_df.empty:
            return None

        # Select a random row
        random_row = untagged_df.sample(n=1).iloc[0]
        return random_row.to_dict()

    def get_random_not_fully_tagged_row_excluding_user(
        self, username: str
    ) -> Optional[Dict[str, Any]]:
        """Get a random row that the specified user hasn't tagged yet."""
        # Ensure data is fresh (5 minute cache)
        self._ensure_fresh_data(max_age_seconds=300)

        if self.df.empty:
            return None

        # Filter rows where user hasn't tagged (Tagger_1 is not the user)
        available_df = self.df[
            (self.df["Tagger_1"].isna())
            | (self.df["Tagger_1"] == "")
            | (self.df["Tagger_1"] != username)
        ]

        if available_df.empty:
            return None

        # Select a random row
        random_row = available_df.sample(n=1).iloc[0]
        return random_row.to_dict()

    def update_record(self, link: str, update_dict: Dict[str, Any]) -> bool:
        """Update a record by its link."""
        if self.df.empty:
            return False

        # Find the record by link
        mask = self.df["Link"] == link
        matching_rows = self.df[mask]

        if matching_rows.empty:
            return False

        # Update the record
        for column, value in update_dict.items():
            if column in self.df.columns:
                self.df.loc[mask, column] = value

        return True

    def add_new_record(self, record_dict: Dict[str, Any]):
        """Add a new record to the DataFrame."""
        # Convert to DataFrame row and append
        new_row = pd.DataFrame([record_dict])
        self.df = pd.concat([self.df, new_row], ignore_index=True)

    def tag_record(self, link: str, username: str, result: int) -> bool:
        """Tag a record with username and result."""
        if self.df.empty:
            return False

        # Find the record by link
        mask = self.df["Link"] == link
        matching_rows = self.df[mask]

        if matching_rows.empty:
            return False

        # Check if already fully tagged
        row = matching_rows.iloc[0]
        if not pd.isna(row["Tagger_1"]) and row["Tagger_1"] != "":
            return False  # Already tagged

        # Update the record
        self.df.loc[mask, "Tagger_1"] = username
        self.df.loc[mask, "Tagger_1_Result"] = result

        return True

    def get_user_tagged_count(self, username: str) -> int:
        """Get count of records tagged by a specific user."""
        if self.df.empty:
            return 0

        return len(self.df[self.df["Tagger_1"] == username])

    # Additional methods to match the existing NarrativesDB interface
    def get_stats(self):
        """Get statistics about the data (for compatibility)."""
        if self.df.empty:
            return {}

        # Group by Sheet and calculate stats
        stats = []
        for sheet_name, group in self.df.groupby("Sheet"):
            total = len(group)
            tagged = len(group[group["Tagger_1"].notna() & (group["Tagger_1"] != "")])

            stats.append(
                {
                    "sheet": sheet_name,
                    "total": total,
                    "tagged": tagged,
                    "remaining": total - tagged,
                }
            )

        return stats

    def get_all_records(self) -> List[Dict[str, Any]]:
        """Get all records as list of dictionaries."""
        if self.df.empty:
            return []

        return self.df.to_dict("records")

    def filter_records(self, **filters) -> List[Dict[str, Any]]:
        """Filter records based on provided criteria."""
        if self.df.empty:
            return []

        filtered_df = self.df.copy()

        for column, value in filters.items():
            if column in filtered_df.columns:
                filtered_df = filtered_df[filtered_df[column] == value]

        return filtered_df.to_dict("records")

    def count_records(self, **filters) -> int:
        """Count records matching the provided criteria."""
        return len(self.filter_records(**filters))

    def _ensure_fresh_data(self, max_age_seconds: int = 60):
        """
        Ensure data is fresh by reloading if it's older than max_age_seconds.

        Args:
            max_age_seconds: Maximum age of data in seconds before refresh
        """
        import time

        current_time = time.time()

        # Initialize last_loaded_time if not exists
        if not hasattr(self, "last_loaded_time"):
            self.last_loaded_time = 0

        # Reload if data is stale
        if current_time - self.last_loaded_time > max_age_seconds:
            logger.info("Data is stale, refreshing from Google Sheets...")
            self.load_data(self.current_sheet_name)
            self.last_loaded_time = current_time
