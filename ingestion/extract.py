import os
import camelot
import pandas as pd
import pdfplumber
import re


class Extract:
    """
    Handles extraction of data from PDF files.
    
    Attributes:
        pdf_path (str): The file path to the source PDF.
    """
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
        current_feature = []

        with pdfplumber.open(self.pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if not text:
                    continue

                # Pre-clean text: handle hyphenation and CID tags
                # Refined to avoid joining if followed by "und" or "oder" (e.g. "Pollen- und Staubfilter")
                text = re.sub(r'(\w+)-\n\s*(?!(?:und|oder)\b)(\w+)', r'\1\2', text)
                
                for line in text.split("\n"):
                    line = line.strip()
                    if not line:
                        continue

                    # Exclude lines starting with engine specs
                    if re.match(r'^\s*\d+\.\d+\s*TSI', line, re.IGNORECASE):
                        # Treat as a separator, reset current feature if needed, or primarily just ignore.
                        # If we hit an engine spec, it's definitely not a continuation of a feature.
                        if current_feature:
                            features.append(" ".join(current_feature))
                            current_feature = []
                        continue

                    # Heuristic: Valid feature lines usually have the checkmarks (cid:127) or start with a bullet.
                    # If we are in the middle of a feature, we allow lines WITHOUT checks as continuations.
                    is_valid_start = self.detect_bullets(line) or "(cid:127)" in line
                    
                    if not is_valid_start and not current_feature:
                        # Skip if it's not a start and we don't have a current feature
                        continue
                    
                    if self.is_new_feature(line):
                        if current_feature:
                            features.append(" ".join(current_feature))
                        current_feature = [line]
                    else:
                        # Continuation
                        current_feature.append(line)
        
        # maintain last feature
        if current_feature:
            features.append(" ".join(current_feature))
            
        # Post-filter to remove fragments that are just noise or common conjunctions
        cleaned_features = []
        noise_words = {"und", "auf", "oder", "mit", "von", "aus"}
        for f in features:
            f_clean = re.sub(r'[\s\-–—\.]+', '', f).lower()
            if f_clean in noise_words or len(f_clean) < 2:
                continue
            cleaned_features.append(f)

        return cleaned_features

    def is_new_feature(self, line: str) -> bool:
        if self.detect_bullets(line):
            return True
        # If no bullet, check capitalization.
        # New features usually start with Uppercase. Wrapped lines (e.g. "und...", "mit...") Start Lowercase.
        # Also clean any weird starting chars?
        clean = line.lstrip()
        if clean and clean[0].islower():
            return False
            
        # Default True (Capital or Symbol or Number)
        return True

    def detect_bullets(self, line: str) -> bool:
        # Common symbols used as bullets or indicators.
        bullets = ["•", "▪", "●", "·"]
        for bullet in bullets:
            if line.lstrip().startswith(bullet):
                return True
        return False


if __name__ == "__main__":
    PDF_PATH = os.path.join("pdf", "Serie Ibiza-1-1-3.pdf")
    extractor = Extract(PDF_PATH)
    tables_df = extractor.extract_tables()
    features = extractor.extract_features()
    print("Extracted Tables DataFrame:")
    print(tables_df)
