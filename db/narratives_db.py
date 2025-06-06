import os
import pandas as pd
import pprint
import datetime
import io


class NarrativesDB:
    def __init__(self, excel_path=None):
        self.excel_path = excel_path
        self.excel_folder = os.path.dirname(excel_path) if excel_path else None
        self.df = pd.DataFrame()
        excel_file = pd.ExcelFile(self.excel_path)
        for sheet in excel_file.sheet_names:
            df_sheet = pd.read_excel(self.excel_path, sheet_name=sheet)
            if not df_sheet.empty:
                df_sheet.insert(0, "Sheet", sheet)
                # Remove Tagger_2 and Tagger_2_Result columns if they exist
                columns_to_drop = ["Tagger_2", "Tagger_2_Result"]
                df_sheet = df_sheet.drop(
                    columns=[col for col in columns_to_drop if col in df_sheet.columns]
                )
                self.df = pd.concat([self.df, df_sheet], ignore_index=True)

    def save_to_excel(self) -> str:
        if self.excel_folder is None:
            raise ValueError("No folder specified to save the Excel file.")
        date_str = datetime.datetime.now().strftime("%Y-%m-%d")
        save_path = os.path.join(self.excel_folder, f"Narrative-{date_str}.xlsx")
        with pd.ExcelWriter(save_path, engine="openpyxl") as writer:
            for sheet_name in self.df["Sheet"].unique():
                df_sheet = self.df[self.df["Sheet"] == sheet_name].drop(
                    columns=["Sheet"]
                )
                # Ensure Tagger_2 columns are not saved
                columns_to_drop = ["Tagger_2", "Tagger_2_Result"]
                df_sheet = df_sheet.drop(
                    columns=[col for col in columns_to_drop if col in df_sheet.columns]
                )
                df_sheet.to_excel(writer, sheet_name=sheet_name, index=False)
        return save_path

    def get_excel_bytes(self) -> bytes:
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            self.df.to_excel(writer, index=False)
        output.seek(0)
        return output.read()

    def get_random_not_fully_tagged_row(self):
        if self.df.empty:
            return None
        # Filter rows where Tagger_1 is 'Init'
        filtered_df = self.df[(self.df["Tagger_1"] == "Init")]
        if filtered_df.empty:
            return None
        random_row = filtered_df.sample()
        row_dict = random_row.iloc[0].to_dict()
        # Convert NaN values to None for proper JSON serialization
        for key, value in row_dict.items():
            if pd.isna(value):
                row_dict[key] = None
        return row_dict

    def update_record(self, link: str, updated_data: dict):
        """Update a record in the database by its link (unique identifier)"""
        if self.df.empty:
            return False

        # Find the record by link
        record_index = self.df[self.df["Link"] == link].index
        if len(record_index) == 0:
            return False

        # Update the record
        for key, value in updated_data.items():
            if key in self.df.columns:
                self.df.loc[record_index[0], key] = value

        return True

    def add_new_record(self, record_data: dict):
        """Add a new record to the database"""
        # Convert to DataFrame row and append
        new_row = pd.DataFrame([record_data])
        self.df = pd.concat([self.df, new_row], ignore_index=True)
        return True

    def save_changes(self):
        """Save changes back to the original Excel file"""
        if self.excel_path is None:
            raise ValueError("No Excel path specified")

        with pd.ExcelWriter(self.excel_path, engine="openpyxl") as writer:
            for sheet_name in self.df["Sheet"].unique():
                df_sheet = self.df[self.df["Sheet"] == sheet_name].drop(
                    columns=["Sheet"]
                )
                # Ensure Tagger_2 columns are not saved
                columns_to_drop = ["Tagger_2", "Tagger_2_Result"]
                df_sheet = df_sheet.drop(
                    columns=[col for col in columns_to_drop if col in df_sheet.columns]
                )
                df_sheet.to_excel(writer, sheet_name=sheet_name, index=False)

        return True

    def get_random_not_fully_tagged_row_excluding_user(self, username: str):
        """Get random row that user hasn't tagged yet"""
        if self.df.empty:
            return None

        # Filter rows where Tagger_1 is 'Init' AND the user is not already a tagger
        filtered_df = self.df[
            (self.df["Tagger_1"] == "Init") & (self.df["Tagger_1"] != username)
        ]

        if filtered_df.empty:
            return None

        random_row = filtered_df.sample()
        row_dict = random_row.iloc[0].to_dict()
        # Convert NaN values to None for proper JSON serialization
        for key, value in row_dict.items():
            if pd.isna(value):
                row_dict[key] = None
        return row_dict

    def get_user_tagged_count(self, username: str):
        """Get count of records tagged by the user"""
        if self.df.empty:
            return 0

        count = len(self.df[(self.df["Tagger_1"] == username)])
        return count

    def tag_record(self, link: str, username: str, result: int):
        """Tag a record with user's name and result"""
        if self.df.empty:
            return False

        # Find the record by link
        record_index = self.df[self.df["Link"] == link].index
        if len(record_index) == 0:
            return False

        row_idx = record_index[0]

        # Check if Tagger_1 field is available
        if self.df.loc[row_idx, "Tagger_1"] == "Init":
            self.df.loc[row_idx, "Tagger_1"] = username
            self.df.loc[row_idx, "Tagger_1_Result"] = result
        else:
            # Tagger is already filled, this shouldn't happen with proper filtering
            return False

        return True


if __name__ == "__main__":
    # Use environment variable for database path to avoid hardcoded production path
    default_path = os.path.join(
        os.path.dirname(__file__), "..", "static", "db", "narratives_db.xlsx"
    )
    excel_path = os.getenv("NARRATIVES_DB_PATH", default_path)

    # Safety check: prevent accidental modification during testing
    if "test" in excel_path.lower() or "temp" in excel_path.lower():
        print(f"🧪 Using test database: {excel_path}")
    else:
        print(f"📊 Using production database: {excel_path}")
        print("⚠️  WARNING: This will use the production database!")

    db = NarrativesDB(excel_path=excel_path)
    print(f"Loaded {len(db.df)} records from database")
    print(db.df.head())
