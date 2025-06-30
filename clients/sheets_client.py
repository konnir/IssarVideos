"""
Google Sheets client for reading and writing data to Google Sheets.
"""

import os
import logging
import pandas as pd
from typing import Optional, Any, List
import gspread
from google.oauth2.service_account import Credentials

logger = logging.getLogger(__name__)


class SheetsClient:
    """Client for Google Sheets operations using service account authentication."""

    def __init__(
        self, credentials_path: Optional[str] = None, sheet_id: Optional[str] = None
    ):
        """
        Initialize the Google Sheets client.

        Args:
            credentials_path: Path to service account JSON file
            sheet_id: Google Sheets document ID
        """
        self.credentials_path = credentials_path or os.getenv(
            "GOOGLE_SHEETS_CREDENTIALS_PATH"
        )
        self.sheet_id = sheet_id or os.getenv(
            "GOOGLE_SHEETS_ID", "1OYF8OH41MiZUEtKA5y8O-vklnVPpYmZUrnNxiIWtryU"
        )

        if not self.credentials_path:
            raise ValueError("Google Sheets credentials path not provided")

        self.client = None
        self.spreadsheet = None
        self._authenticate()

    def _authenticate(self):
        """Authenticate with Google Sheets API using service account."""
        try:
            # Define the scope for Google Sheets and Drive APIs
            scope = [
                "https://spreadsheets.google.com/feeds",
                "https://www.googleapis.com/auth/drive",
            ]

            # Load credentials from JSON file
            creds = Credentials.from_service_account_file(
                self.credentials_path, scopes=scope
            )

            # Create the gspread client
            self.client = gspread.authorize(creds)

            # Open the spreadsheet
            self.spreadsheet = self.client.open_by_key(self.sheet_id)

            logger.info(
                f"Successfully authenticated with Google Sheets: {self.sheet_id}"
            )

        except Exception as e:
            logger.error(f"Failed to authenticate with Google Sheets: {str(e)}")
            raise

    def get_worksheet(self, sheet_name: str = None):
        """
        Get a specific worksheet by name, or the first worksheet if no name provided.
        If the named worksheet doesn't exist, it will be created.

        Args:
            sheet_name: Name of the worksheet

        Returns:
            gspread Worksheet object
        """
        try:
            if sheet_name:
                return self.spreadsheet.worksheet(sheet_name)
            else:
                return self.spreadsheet.sheet1  # First sheet
        except gspread.WorksheetNotFound:
            if sheet_name:
                logger.info(f"Worksheet '{sheet_name}' not found. Creating new worksheet.")
                return self.create_worksheet(sheet_name)
            else:
                logger.error(f"Default worksheet not found")
                raise

    def read_sheet_to_dataframe(self, sheet_name: str = None) -> pd.DataFrame:
        """
        Read a Google Sheet and return as pandas DataFrame.

        Args:
            sheet_name: Name of the worksheet to read

        Returns:
            pandas DataFrame with the sheet data
        """
        try:
            worksheet = self.get_worksheet(sheet_name)

            # Get all records as list of dictionaries
            records = worksheet.get_all_records()

            if not records:
                logger.warning(f"No data found in worksheet '{sheet_name}'")
                return pd.DataFrame()

            # Convert to DataFrame
            df = pd.DataFrame(records)

            logger.info(
                f"Successfully read {len(df)} rows from worksheet '{sheet_name}'"
            )
            return df

        except Exception as e:
            logger.error(f"Failed to read sheet to DataFrame: {str(e)}")
            raise

    def write_dataframe_to_sheet(
        self, df: pd.DataFrame, sheet_name: str = None, clear_sheet: bool = True
    ):
        """
        Write a pandas DataFrame to Google Sheet.

        Args:
            df: pandas DataFrame to write
            sheet_name: Name of the worksheet to write to
            clear_sheet: Whether to clear the sheet before writing
        """
        try:
            worksheet = self.get_worksheet(sheet_name)

            if clear_sheet:
                worksheet.clear()

            # Convert DataFrame to list of lists (including headers)
            data = [df.columns.tolist()] + df.fillna("").values.tolist()

            # Update the worksheet with the data
            worksheet.update(data, value_input_option="USER_ENTERED")

            logger.info(
                f"Successfully wrote {len(df)} rows to worksheet '{sheet_name}'"
            )

        except Exception as e:
            logger.error(f"Failed to write DataFrame to sheet: {str(e)}")
            raise

    def append_row_to_sheet(self, row_data: List[Any], sheet_name: str = None):
        """
        Append a single row to the Google Sheet.

        Args:
            row_data: List of values to append as a new row
            sheet_name: Name of the worksheet
        """
        try:
            worksheet = self.get_worksheet(sheet_name)
            worksheet.append_row(row_data, value_input_option="USER_ENTERED")

            logger.info(f"Successfully appended row to worksheet '{sheet_name}'")

        except Exception as e:
            logger.error(f"Failed to append row to sheet: {str(e)}")
            raise

    def update_cell(self, row: int, col: int, value: Any, sheet_name: str = None):
        """
        Update a specific cell in the Google Sheet.

        Args:
            row: Row number (1-indexed)
            col: Column number (1-indexed)
            value: Value to set
            sheet_name: Name of the worksheet
        """
        try:
            worksheet = self.get_worksheet(sheet_name)
            worksheet.update_cell(row, col, value)

            logger.info(
                f"Successfully updated cell ({row}, {col}) in worksheet '{sheet_name}'"
            )

        except Exception as e:
            logger.error(f"Failed to update cell: {str(e)}")
            raise

    def get_all_worksheets(self) -> List[str]:
        """
        Get list of all worksheet names in the spreadsheet.

        Returns:
            List of worksheet names
        """
        try:
            return [ws.title for ws in self.spreadsheet.worksheets()]
        except Exception as e:
            logger.error(f"Failed to get worksheet names: {str(e)}")
            raise

    def create_worksheet(self, sheet_name: str, rows: int = 1000, cols: int = 26):
        """
        Create a new worksheet in the spreadsheet.

        Args:
            sheet_name: Name for the new worksheet
            rows: Number of rows (default: 1000)
            cols: Number of columns (default: 26)
        """
        try:
            worksheet = self.spreadsheet.add_worksheet(
                title=sheet_name, rows=rows, cols=cols
            )

            logger.info(f"Successfully created worksheet '{sheet_name}'")
            return worksheet

        except Exception as e:
            logger.error(f"Failed to create worksheet '{sheet_name}': {str(e)}")
            raise

    def validate_connection(self) -> bool:
        """
        Validate the connection to Google Sheets.

        Returns:
            True if connection is valid, False otherwise
        """
        try:
            # Try to get spreadsheet info
            info = self.spreadsheet.title
            logger.info(f"Connection validated. Spreadsheet title: {info}")
            return True
        except Exception as e:
            logger.error(f"Connection validation failed: {str(e)}")
            return False
