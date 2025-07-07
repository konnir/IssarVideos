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
        self.last_loaded_time = None
        # Track row positions for cell-level updates
        self._row_positions = {}  # {(sheet_name, link): row_number}
        self._row_mapping_built = False  # Track if mapping has been built
        # Load data from all sheets by default for tagging management
        self.load_all_sheets_data()

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
            
            # Clean up the dataframe - remove empty column names
            if not self.df.empty:
                valid_columns = [col for col in self.df.columns if col and str(col).strip()]
                self.df = self.df[valid_columns]
                
            # Update timestamp
            import time
            self.last_loaded_time = time.time()

            # Don't build row position mapping immediately to reduce startup API calls
            # It will be built on-demand when needed for cell updates
            self._row_mapping_built = False

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

    def load_all_sheets_data(self):
        """
        Load data from ALL worksheets and combine them into a single DataFrame.
        This is needed for the tagging management table to show all sheets.
        """
        try:
            # Get all worksheets
            worksheets = self.sheets_client.get_all_worksheets()
            if not worksheets:
                logger.warning("No worksheets found in the spreadsheet")
                return

            # List to collect DataFrames from all sheets
            all_dfs = []

            for sheet_name in worksheets:
                try:
                    logger.info(f"Loading data from sheet: {sheet_name}")
                    sheet_df = self.sheets_client.read_sheet_to_dataframe(sheet_name)

                    if not sheet_df.empty:
                        # Clean up the dataframe - remove empty column names
                        # Get column names that are not empty or just whitespace
                        valid_columns = [col for col in sheet_df.columns if col and str(col).strip()]
                        sheet_df = sheet_df[valid_columns]
                        
                        # Add/update the Sheet column with the actual sheet name
                        sheet_df["Sheet"] = sheet_name
                        all_dfs.append(sheet_df)
                        logger.info(
                            f"Loaded {len(sheet_df)} records from sheet '{sheet_name}'"
                        )
                    else:
                        logger.warning(f"Sheet '{sheet_name}' is empty")

                except Exception as e:
                    logger.error(
                        f"Failed to load data from sheet '{sheet_name}': {str(e)}"
                    )
                    continue

            # Combine all DataFrames
            if all_dfs:
                self.df = pd.concat(all_dfs, ignore_index=True)
                logger.info(
                    f"Successfully loaded {len(self.df)} total records from {len(all_dfs)} sheets"
                )
            else:
                logger.warning("No data loaded from any sheets")
                self.df = pd.DataFrame(
                    columns=[
                        "Sheet",
                        "Narrative",
                        "Story",
                        "Link",
                        "Tagger_1",
                        "Tagger_1_Result",
                    ]
                )  # Update timestamp
            import time

            self.last_loaded_time = time.time()

            # Don't build row position mapping immediately to reduce startup API calls
            # It will be built on-demand when needed for cell updates
            self._row_mapping_built = False

        except Exception as e:
            logger.error(f"Failed to load data from all sheets: {str(e)}")
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

    def _build_row_position_mapping(self):
        """Build mapping of (sheet_name, link) to row positions for cell-level updates using existing DataFrame."""
        self._row_positions = {}

        if self.df.empty:
            return

        try:
            # Group by sheet to get row positions within each sheet
            for sheet_name, group_df in self.df.groupby("Sheet"):
                # Sort by index to maintain consistent ordering
                sorted_group = group_df.sort_index()

                # Calculate row positions based on DataFrame index
                # Row position = current count of records in this sheet + 2 (for 1-indexing and header)
                for local_idx, (_, row) in enumerate(sorted_group.iterrows(), start=2):
                    link = row.get("Link")
                    if pd.notna(link) and link != "":
                        self._row_positions[(sheet_name, link)] = local_idx

            logger.info(
                f"Built row position mapping for {len(self._row_positions)} records (using DataFrame)"
            )

        except Exception as e:
            logger.error(f"Failed to build row position mapping: {str(e)}")
            self._row_positions = {}

    def save_changes(self):
        """Save the current DataFrame back to Google Sheets, distributing records to their respective sheets."""
        try:
            if self.df.empty:
                logger.warning("No data to save")
                return

            # Group records by their Sheet column and save each group to its respective sheet
            for sheet_name, group_df in self.df.groupby("Sheet"):
                logger.info(f"Saving {len(group_df)} records to sheet '{sheet_name}'")

                # Remove the Sheet column before writing since it's redundant
                # (the sheet name is already determined by where we're writing)
                save_df = group_df.drop(columns=["Sheet"]).copy()

                self.sheets_client.write_dataframe_to_sheet(
                    save_df, sheet_name, clear_sheet=True
                )

            logger.info(
                f"Successfully saved {len(self.df)} records across {len(self.df.groupby('Sheet'))} sheets"
            )

        except Exception as e:
            logger.error(f"Failed to save changes to Google Sheets: {str(e)}")
            raise

    def add_record_to_specific_sheet(self, record_dict: Dict[str, Any]):
        """Add a new record to the specific sheet mentioned in the record."""
        try:
            target_sheet = record_dict.get("Sheet")
            if not target_sheet:
                raise ValueError("Sheet name is required in record_dict")

            logger.info(f"Adding record to sheet: {target_sheet}")

            # Read current data from the target sheet
            try:
                sheet_df = self.sheets_client.read_sheet_to_dataframe(target_sheet)
                logger.info(
                    f"Read {len(sheet_df)} existing records from sheet '{target_sheet}'"
                )
            except Exception as e:
                # If sheet doesn't exist or is empty, create new DataFrame
                logger.info(f"Creating new sheet or sheet is empty: {target_sheet}")
                sheet_df = pd.DataFrame(
                    columns=[
                        "Sheet",
                        "Narrative",
                        "Story",
                        "Link",
                        "Tagger_1",
                        "Tagger_1_Result",
                    ]
                )

            # Ensure the Sheet column has the correct value
            record_dict["Sheet"] = target_sheet

            # Add the new record
            new_row = pd.DataFrame([record_dict])
            sheet_df = pd.concat([sheet_df, new_row], ignore_index=True)

            # Write back to the specific sheet
            self.sheets_client.write_dataframe_to_sheet(
                sheet_df, target_sheet, clear_sheet=True
            )

            logger.info(
                f"Successfully added record to sheet '{target_sheet}'. New total: {len(sheet_df)} records"
            )

            # Also add to our main DataFrame for immediate consistency
            self.df = pd.concat([self.df, new_row], ignore_index=True)

            return True

        except Exception as e:
            logger.error(f"Failed to add record to sheet '{target_sheet}': {str(e)}")
            raise

    def add_record_to_specific_sheet_append(self, record_dict: Dict[str, Any]) -> bool:
        """Add a new record to a specific sheet using append operation."""
        try:
            target_sheet = record_dict.get("Sheet")
            if not target_sheet:
                raise ValueError("Sheet name is required in record_dict")

            logger.info(f"Adding record to sheet using append: {target_sheet}")

            # Ensure the Sheet column has the correct value
            record_dict["Sheet"] = target_sheet

            # Prepare row data in the correct column order
            expected_columns = [
                "Sheet",
                "Narrative",
                "Story",
                "Link",
                "Tagger_1",
                "Tagger_1_Result",
            ]
            row_data = []

            for col in expected_columns:
                value = record_dict.get(col, "")
                # Convert None to empty string for sheets
                if value is None:
                    value = ""
                row_data.append(value)

            # Append to the specific sheet
            self.sheets_client.append_row_to_sheet(row_data, target_sheet)

            # Add to our local DataFrame for immediate consistency
            new_row = pd.DataFrame([record_dict])
            self.df = pd.concat([self.df, new_row], ignore_index=True)

            # Update row position mapping for this new record
            # Calculate new row position based on existing records count in this sheet
            existing_records_in_sheet = len(self.df[self.df["Sheet"] == target_sheet])
            new_row_position = existing_records_in_sheet + 1  # +1 for header row
            link = record_dict.get("Link")
            if link:
                self._row_positions[(target_sheet, link)] = new_row_position

            logger.info(
                f"Successfully added record to sheet '{target_sheet}' using append"
            )
            return True

        except Exception as e:
            logger.error(
                f"Failed to add record to sheet '{target_sheet}' using append: {str(e)}"
            )
            return False

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

    def tag_record_cell_update(self, link: str, username: str, result: int) -> bool:
        """Tag a record using cell-level updates instead of full sheet rewrite."""
        if self.df.empty:
            return False

        # Find the record by link in our DataFrame
        mask = self.df["Link"] == link
        matching_rows = self.df[mask]

        if matching_rows.empty:
            return False

        # Check if already fully tagged
        row = matching_rows.iloc[0]
        if not pd.isna(row["Tagger_1"]) and row["Tagger_1"] != "":
            return False  # Already tagged

        # Get the sheet name for this record
        sheet_name = row["Sheet"]

        # Ensure row position mapping is built
        self._ensure_row_mapping_built()

        # Find row position in the sheet
        row_key = (sheet_name, link)
        if row_key not in self._row_positions:
            logger.warning(
                f"Row position not found for link {link} in sheet {sheet_name}"
            )
            return False

        row_position = self._row_positions[row_key]

        try:
            # Get dynamic column mapping
            column_mapping = self.sheets_client.get_column_mapping(sheet_name)

            if (
                "Tagger_1" not in column_mapping
                or "Tagger_1_Result" not in column_mapping
            ):
                logger.error(f"Required columns not found in sheet {sheet_name}")
                return False

            tagger_col = column_mapping["Tagger_1"]
            result_col = column_mapping["Tagger_1_Result"]

            # Prepare batch update
            updates = [
                {"row": row_position, "col": tagger_col, "value": username},
                {"row": row_position, "col": result_col, "value": result},
            ]

            # Perform batch cell update
            self.sheets_client.update_cells_batch(updates, sheet_name)

            # Update our local DataFrame
            self.df.loc[mask, "Tagger_1"] = username
            self.df.loc[mask, "Tagger_1_Result"] = result

            logger.info(f"Successfully tagged record using cell-level update: {link}")
            return True

        except Exception as e:
            logger.error(f"Failed to tag record with cell-level update: {str(e)}")
            return False

    def update_record_cell_update(self, link: str, update_dict: Dict[str, Any]) -> bool:
        """Update a record using cell-level updates instead of full sheet rewrite."""
        if self.df.empty:
            return False

        # Find the record by link
        mask = self.df["Link"] == link
        matching_rows = self.df[mask]

        if matching_rows.empty:
            return False

        # Get the sheet name for this record
        row = matching_rows.iloc[0]
        sheet_name = row["Sheet"]

        # Ensure row position mapping is built
        self._ensure_row_mapping_built()

        # Find row position in the sheet
        row_key = (sheet_name, link)
        if row_key not in self._row_positions:
            logger.warning(
                f"Row position not found for link {link} in sheet {sheet_name}"
            )
            return False

        row_position = self._row_positions[row_key]

        try:
            # Get dynamic column mapping
            column_mapping = self.sheets_client.get_column_mapping(sheet_name)

            # Prepare batch update
            updates = []
            for column, value in update_dict.items():
                if column in column_mapping and column in self.df.columns:
                    col_position = column_mapping[column]
                    updates.append(
                        {"row": row_position, "col": col_position, "value": value}
                    )

            if not updates:
                logger.warning("No valid columns to update")
                return False

            # Perform batch cell update
            self.sheets_client.update_cells_batch(updates, sheet_name)

            # Update our local DataFrame
            for column, value in update_dict.items():
                if column in self.df.columns:
                    self.df.loc[mask, column] = value

            logger.info(f"Successfully updated record using cell-level update: {link}")
            return True

        except Exception as e:
            logger.error(f"Failed to update record with cell-level update: {str(e)}")
            return False

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

    def add_new_record_append(self, record_dict: Dict[str, Any]) -> bool:
        """Add a new record using append operation instead of full sheet rewrite."""
        try:
            target_sheet = record_dict.get("Sheet")
            if not target_sheet:
                target_sheet = self.current_sheet_name or "Sheet1"
                record_dict["Sheet"] = target_sheet

            # Prepare row data in the correct column order
            # Ensure we match the expected column structure
            expected_columns = [
                "Sheet",
                "Narrative",
                "Story",
                "Link",
                "Tagger_1",
                "Tagger_1_Result",
            ]
            row_data = []

            for col in expected_columns:
                value = record_dict.get(col, "")
                # Convert None to empty string for sheets
                if value is None:
                    value = ""
                row_data.append(value)

            # Append to the specific sheet
            self.sheets_client.append_row_to_sheet(row_data, target_sheet)

            # Add to our local DataFrame
            new_row = pd.DataFrame([record_dict])
            self.df = pd.concat([self.df, new_row], ignore_index=True)

            # Update row position mapping for this new record
            # Calculate new row position based on existing records count in this sheet
            existing_records_in_sheet = len(self.df[self.df["Sheet"] == target_sheet])
            new_row_position = existing_records_in_sheet + 1  # +1 for header row
            link = record_dict.get("Link")
            if link:
                self._row_positions[(target_sheet, link)] = new_row_position

            logger.info(f"Successfully added new record using append: {link}")
            return True

        except Exception as e:
            logger.error(f"Failed to add new record using append: {str(e)}")
            return False

    def _ensure_row_mapping_built(self):
        """Ensure row position mapping is built when needed for cell operations."""
        if not self._row_mapping_built:
            logger.info("Building row position mapping on-demand...")
            self._build_row_position_mapping()
            self._row_mapping_built = True
