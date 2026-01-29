from ingestion.extract import Extract
import os

PDF_PATH = os.path.join("pdf", "Serie Ibiza-1-1-3.pdf")

extractor = Extract(PDF_PATH)

tables_df = extractor.extract_tables()
features = extractor.extract_features()

