from ingestion.extract import Extract
from ingestion.transform import Transform
from ingestion.load import Load
import os

PDF_PATH = os.path.join("pdf", "Serie Ibiza-1-1-3.pdf")
OUTPUT_PATH = os.path.join("excel", "output.xlsx")

extractor = Extract(PDF_PATH)

tables_df = extractor.extract_tables()
features = extractor.extract_features()

transformer = Transform(tables_df, features)
final_df = transformer.run()
print("Final Transformed DataFrame columns:")
print(final_df.columns.tolist())
print("Final Transformed DataFrame:")
print(final_df)

loader = Load(final_df, OUTPUT_PATH)
loader.to_excel()

