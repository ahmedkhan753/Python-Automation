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
            
            # Use xlsxwriter engine for formatting
            writer = pd.ExcelWriter(self.output_path, engine='xlsxwriter')
            self.data.to_excel(writer, index=False, sheet_name='Sheet1')

            workbook = writer.book
            worksheet = writer.sheets['Sheet1']

            # Define Red Format
            red_format = workbook.add_format({'bg_color': '#FFC7CE', 'font_color': '#9C0006'})

            # Apply Conditional Formatting for "N/A"
            worksheet.conditional_format(1, 0, self.data.shape[0], self.data.shape[1] - 1, {
                'type': 'cell',
                'criteria': 'equal to',
                'value': '"N/A"',
                'format': red_format
            })

            # Also cover "( not specified )" just in case
            worksheet.conditional_format(1, 0, self.data.shape[0], self.data.shape[1] - 1, {
                'type': 'cell',
                'criteria': 'equal to',
                'value': '"( not specified )"',
                'format': red_format
            })

            writer.close()
            print(f"File saved to {self.output_path} with formatting.")
        except Exception as e:
            print(f"Error saving to Excel: {e}")
