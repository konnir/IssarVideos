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
                df_sheet.insert(0, 'Sheet', sheet)
                self.df = pd.concat([self.df, df_sheet], ignore_index=True)

    def save_to_excel(self) -> str:
        if self.excel_folder is None:
            raise ValueError("No folder specified to save the Excel file.")
        date_str = datetime.datetime.now().strftime("%Y-%m-%d")
        save_path = os.path.join(self.excel_folder, f"Narrative-{date_str}.xlsx")
        with pd.ExcelWriter(save_path, engine='openpyxl') as writer:
            for sheet_name in self.df['Sheet'].unique():
                df_sheet = self.df[self.df['Sheet'] == sheet_name].drop(columns=['Sheet'])
                df_sheet.to_excel(writer, sheet_name=sheet_name, index=False)
        return save_path
    
    def get_excel_bytes(self) -> bytes:
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            self.df.to_excel(writer, index=False)
        output.seek(0)
        return output.read()


        
if __name__ == "__main__":
    excel_path = os.path.join(os.path.dirname(__file__), '/Users/nirkon/free_dev/IssarVideos/static/narratives_db.xlsx')
    db = NarrativesDB(excel_path=excel_path)    
    print(db.df)
