import os
import io
import pandas as pd
from skills.base_skill import BaseSkill


class SpreadsheetAnalyzerSkill(BaseSkill):
    name: str = "spreadsheet_analyzer"
    description: str = "Reads and analyzes excel/csv files, returns stats and sample data."
    version: str = "1.0.0"

    def execute(self, input_text: str, **kwargs) -> str:
        """
        Input format: filepath (can also accept a question via kwargs or parsed from input, 
        but we'll keep it simple: if there's a '|', split path and question).
        """
        if not self.validate_input(input_text):
            return "Invalid input."

        # Support optional question: "path/to/file.csv | what is the average of column X?"
        parts = [p.strip() for p in input_text.split('|', 1)]
        filepath = parts[0]
        question = parts[1] if len(parts) > 1 else None

        if not os.path.exists(filepath):
            return f"Error: File '{filepath}' does not exist."

        try:
            if filepath.endswith('.csv'):
                df = pd.read_csv(filepath)
            elif filepath.endswith('.xlsx') or filepath.endswith('.xls'):
                df = pd.read_excel(filepath)
            else:
                return "Error: Unsupported file format. Use .csv or .xlsx"

            buf = io.StringIO()
            
            # Basic stats and first 10 rows
            buf.write(f"--- DataFrame Summary ---\n")
            buf.write(f"Shape: {df.shape[0]} rows, {df.shape[1]} columns\n\n")
            
            buf.write("--- Columns ---\n")
            for col in df.columns:
                buf.write(f"- {col} (dtype: {df[col].dtype})\n")
            buf.write("\n")

            buf.write("--- Descriptive Statistics ---\n")
            df.describe().to_csv(buf)
            buf.write("\n")
            
            buf.write("--- First 10 Rows ---\n")
            df.head(10).to_csv(buf, index=False)
            
            output = buf.getvalue()
            
            if question:
                output += f"\n\n[Note: To answer '{question}', the LLM should analyze the data above.]"
                
            return output
        except Exception as e:
            return f"Error analyzing spreadsheet: {str(e)}"
