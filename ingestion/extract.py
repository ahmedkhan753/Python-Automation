import os
import camelot
import pandas as pd
import pdfplumber
import re


class Extract:
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path

    def extract_tables(self) -> pd.DataFrame:
        combined_df = pd.DataFrame()  # Initialize to empty DataFrame
        try:
            tables = camelot.read_pdf(self.pdf_path, pages="all", flavor="stream")
            if tables:
                dfs = [table.df for table in tables]
                combined_df = pd.concat(dfs, ignore_index=True)
        except Exception as e:
            print(f"Error extracting tables: {e}")
        return combined_df

    def extract_features(self) -> list:
        features = []
        with pdfplumber.open(self.pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    # Pre-clean text: handle hyphenation and CID tags
                    text = re.sub(r'(\w+)-\n\s*(\w+)', r'\1\2', text)
                    text = re.sub(r'\(cid:\d+\)', '', text)
                    
                    for line in text.split("\n"):
                        # Only keep lines that have a bullet AND don't look like engine specs
                        if self.detect_bullets(line):
                            # Exclude lines starting with engine specs like "1.0 TSI" or "1.5 TSI"
                            if re.match(r'^\s*\d+\.\d+\s*TSI', line, re.IGNORECASE):
                                continue
                            
                            # Final clean for the specific line
                            clean_line = re.sub(r'\(cid:\d+\)', '', line)
                            features.append(clean_line.strip())
        return features

    def detect_bullets(self, line: str) -> bool:
        bullets = ["•", "▪", "●"]
        return any(bullet in line for bullet in bullets)


if __name__ == "__main__":
    PDF_PATH = os.path.join("pdf", "Serie Ibiza-1-1-3.pdf")
    extractor = Extract(PDF_PATH)
    tables_df = extractor.extract_tables()
    features = extractor.extract_features()
    print("Extracted Tables DataFrame:")
    print(tables_df)
