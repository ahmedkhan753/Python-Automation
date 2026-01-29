import pandas as pd
import os

class Load:
    def __init__(self, data: pd.DataFrame, output_path: str):
        self.data = data
        self.output_path = output_path

    def to_excel(self):
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.output_path), exist_ok=True)
            
            self.data.to_excel(self.output_path, index=False)
            print(f"File saved to {self.output_path}")
        except Exception as e:
            print(f"Error saving to Excel: {e}")
