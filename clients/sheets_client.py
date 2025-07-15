"""
Google Sheets client for reading and writing data to Google Sheets.
"""

import os
import logging
import pandas as pd
from typing import Optional, Any, List, Dict
import gspread
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

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

        self.client = None
        self.spreadsheet = None
        self._authenticate()

    def _authenticate(self):
        """Authenticate with Google Sheets API using service account or default credentials."""
        try:
            # Define the scope for Google Sheets and Drive APIs
            scope = [
                "https://spreadsheets.google.com/feeds",
                "https://www.googleapis.com/auth/drive",
            ]

            # Use credentials file if provided and exists, otherwise use default credentials
            if self.credentials_path and os.path.exists(self.credentials_path):
                logger.info(f"Using credentials file: {self.credentials_path}")
                creds = Credentials.from_service_account_file(
                    self.credentials_path, scopes=scope
                )
            else:
                logger.info("Using default credentials (Cloud Run service account)")
                from google.auth import default

                creds, _ = default(scopes=scope)

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
                logger.info(
                    f"Worksheet '{sheet_name}' not found. Creating new worksheet."
                )
                # Create worksheet with proper headers for narrative data
                headers = [
                    "Sheet",
                    "Narrative",
                    "Story",
                    "Link",
                    "Tagger_1",
                    "Tagger_1_Result",
                ]
                return self.create_worksheet_with_headers(sheet_name, headers)
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

            # Find the next empty row to ensure we start at column A
            # Get all values to find the last used row
            all_values = worksheet.get_all_values()
            next_row = len(all_values) + 1

            # Update the range starting from column A of the next row
            start_cell = f"A{next_row}"
            end_col_letter = chr(ord("A") + len(row_data) - 1)  # Calculate end column
            end_cell = f"{end_col_letter}{next_row}"
            range_name = f"{start_cell}:{end_cell}"

            # Update the specific range with our row data
            worksheet.update(range_name, [row_data], value_input_option="USER_ENTERED")

            logger.info(
                f"Successfully appended row to worksheet '{sheet_name}' at row {next_row} (range: {range_name})"
            )

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

    def update_cells_batch(self, updates: List[dict], sheet_name: str = None):
        """
        Update multiple cells in a single batch operation.

        Args:
            updates: List of dictionaries with 'row', 'col', 'value' keys
            sheet_name: Name of the worksheet
        """
        try:
            worksheet = self.get_worksheet(sheet_name)

            # Prepare batch update data
            cell_list = []
            for update in updates:
                cell = worksheet.cell(update["row"], update["col"])
                cell.value = update["value"]
                cell_list.append(cell)

            # Perform batch update
            worksheet.update_cells(cell_list)

            logger.info(
                f"Successfully updated {len(updates)} cells in worksheet '{sheet_name}'"
            )

        except Exception as e:
            logger.error(f"Failed to update cells in batch: {str(e)}")
            raise

    def find_row_by_column_value(
        self, search_column: str, search_value: Any, sheet_name: str = None
    ) -> Optional[int]:
        """
        Find the row number of a record by searching for a value in a specific column.

        Args:
            search_column: Column name to search in
            search_value: Value to search for
            sheet_name: Name of the worksheet

        Returns:
            Row number (1-indexed) if found, None otherwise
        """
        try:
            worksheet = self.get_worksheet(sheet_name)

            # Get all values to search through
            all_values = worksheet.get_all_values()
            if not all_values:
                return None

            # Find header row to get column index
            headers = all_values[0]
            if search_column not in headers:
                logger.warning(
                    f"Column '{search_column}' not found in worksheet '{sheet_name}'"
                )
                return None

            col_index = headers.index(search_column)

            # Search for the value (starting from row 2, skipping header)
            for row_index, row_data in enumerate(all_values[1:], start=2):
                if col_index < len(row_data) and row_data[col_index] == str(
                    search_value
                ):
                    return row_index

            return None

        except Exception as e:
            logger.error(f"Failed to find row by column value: {str(e)}")
            raise

    def get_column_mapping(self, sheet_name: str = None) -> Dict[str, int]:
        """
        Get mapping of column names to column numbers for a sheet.

        Args:
            sheet_name: Name of the worksheet

        Returns:
            Dictionary mapping column names to column numbers (1-indexed)
        """
        try:
            worksheet = self.get_worksheet(sheet_name)

            # Get the first row (headers)
            headers = worksheet.row_values(1)

            # Create mapping
            column_mapping = {}
            for idx, header in enumerate(headers, start=1):
                if header:  # Skip empty headers
                    column_mapping[header] = idx

            return column_mapping

        except Exception as e:
            logger.error(f"Failed to get column mapping: {str(e)}")
            return {}

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

    def create_worksheet_with_headers(
        self, sheet_name: str, headers: list, rows: int = 1000, cols: int = 26
    ):
        """
        Create a new worksheet in the spreadsheet with specified headers.

        Args:
            sheet_name: Name for the new worksheet
            headers: List of header names to put in the first row
            rows: Number of rows (default: 1000)
            cols: Number of columns (default: 26)
        """
        try:
            # Create the worksheet
            worksheet = self.create_worksheet(sheet_name, rows, cols)

            # Add headers to the first row
            if headers:
                worksheet.update("1:1", [headers])
                logger.info(f"Added headers to worksheet '{sheet_name}': {headers}")

            return worksheet

        except Exception as e:
            logger.error(
                f"Failed to create worksheet '{sheet_name}' with headers: {str(e)}"
            )
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

    def delete_worksheet(self, sheet_name: str):
        """
        Delete a worksheet from the spreadsheet.

        Args:
            sheet_name: Name of the worksheet to delete
        """
        try:
            # Find the worksheet to delete
            worksheet = None
            for ws in self.spreadsheet.worksheets():
                if ws.title == sheet_name:
                    worksheet = ws
                    break

            if worksheet is None:
                logger.warning(f"Worksheet '{sheet_name}' not found for deletion")
                return False

            # Delete the worksheet
            self.spreadsheet.del_worksheet(worksheet)
            logger.info(f"Successfully deleted worksheet '{sheet_name}'")
            return True

        except Exception as e:
            logger.error(f"Failed to delete worksheet '{sheet_name}': {str(e)}")
            raise

    def batch_read_sheets_to_dataframes(
        self, sheet_names: List[str]
    ) -> Dict[str, pd.DataFrame]:
        """
        Read multiple sheets in a single batch API call and return as DataFrames.

        Args:
            sheet_names: List of worksheet names to read

        Returns:
            Dictionary mapping sheet names to their DataFrames
        """
        try:
            if not sheet_names:
                return {}

            # Create ranges for each sheet (entire sheet)
            ranges = [f"'{sheet_name}'" for sheet_name in sheet_names]

            # Use the underlying Google Sheets API client for batch operations
            from google.oauth2.service_account import Credentials

            # Get credentials (reuse authentication logic)
            scope = [
                "https://spreadsheets.google.com/feeds",
                "https://www.googleapis.com/auth/drive",
            ]

            if self.credentials_path and os.path.exists(self.credentials_path):
                creds = Credentials.from_service_account_file(
                    self.credentials_path, scopes=scope
                )
            else:
                from google.auth import default

                creds, _ = default(scopes=scope)

            # Build the Sheets API service
            service = build("sheets", "v4", credentials=creds)

            # Make batch request
            result = (
                service.spreadsheets()
                .values()
                .batchGet(
                    spreadsheetId=self.sheet_id,
                    ranges=ranges,
                    valueRenderOption="FORMATTED_VALUE",
                    dateTimeRenderOption="FORMATTED_STRING",
                )
                .execute()
            )

            # Process results into DataFrames
            dataframes = {}
            value_ranges = result.get("valueRanges", [])

            for i, sheet_name in enumerate(sheet_names):
                if i < len(value_ranges):
                    values = value_ranges[i].get("values", [])

                    if values:
                        # First row is headers
                        headers = values[0] if values else []
                        data_rows = values[1:] if len(values) > 1 else []

                        # Create DataFrame
                        if headers and data_rows:
                            # Pad rows to match header length
                            max_cols = len(headers)
                            padded_rows = []
                            for row in data_rows:
                                padded_row = row + [""] * (max_cols - len(row))
                                padded_rows.append(padded_row[:max_cols])

                            df = pd.DataFrame(padded_rows, columns=headers)
                            dataframes[sheet_name] = df
                            logger.info(
                                f"Batch read {len(df)} rows from sheet '{sheet_name}'"
                            )
                        else:
                            dataframes[sheet_name] = pd.DataFrame()
                            logger.warning(f"No data found in sheet '{sheet_name}'")
                    else:
                        dataframes[sheet_name] = pd.DataFrame()
                        logger.warning(f"No data found in sheet '{sheet_name}'")
                else:
                    dataframes[sheet_name] = pd.DataFrame()
                    logger.warning(f"No response data for sheet '{sheet_name}'")

            logger.info(
                f"Successfully batch read {len(dataframes)} sheets in single API call"
            )
            return dataframes

        except Exception as e:
            logger.error(f"Failed to batch read sheets: {str(e)}")
            # Fallback to individual reads if batch fails
            logger.info("Falling back to individual sheet reads")
            dataframes = {}
            for sheet_name in sheet_names:
                try:
                    dataframes[sheet_name] = self.read_sheet_to_dataframe(sheet_name)
                except Exception as individual_error:
                    logger.error(
                        f"Failed to read sheet '{sheet_name}': {individual_error}"
                    )
                    dataframes[sheet_name] = pd.DataFrame()
            return dataframes
