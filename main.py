from ingestion.extract import Extract
from ingestion.transform import Transform
import os

PDF_PATH = os.path.join("pdf", "Serie Ibiza-1-1-3.pdf")

extractor = Extract(PDF_PATH)

tables_df = extractor.extract_tables()
features = extractor.extract_features()

transformer = Transform(tables_df, features)
final_df = transformer.run()
print("Final Transformed DataFrame:")
print(final_df)

