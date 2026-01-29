# 🚗 Python PDF to Excel ETL Automation

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An automated ETL (Extract, Transform, Load) pipeline written in Python for processing PDF documents containing car specifications, specifically designed for SEAT Serie Ibiza models. This tool extracts tables and features from PDFs, transforms the data through cleaning and normalization, and outputs structured Excel files with conditional formatting.

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Dependencies](#dependencies)
- [How to Run](#how-to-run)
- [Output Description](#output-description)
- [Contributing](#contributing)
- [License](#license)

## 📖 Overview

This project automates the extraction of vehicle specification data from PDF documents. It uses advanced libraries like Camelot for table extraction and PDFPlumber for text feature extraction. The transformation phase includes data cleaning, normalization, feature categorization, and German-to-English translation. Finally, the processed data is loaded into an Excel file with visual formatting to highlight missing values.

The pipeline is modular, with separate classes for each ETL stage, making it easy to extend or modify for other PDF processing tasks.

## ✨ Features

- **Table Extraction**: Automatically extracts tabular data from PDFs using Camelot's stream flavor for complex layouts.
- **Feature Extraction**: Identifies and extracts bullet-point features from PDF text using PDFPlumber.
- **Data Cleaning**: Removes noise, handles missing values, and normalizes column names.
- **Feature Processing**: Categorizes features (e.g., Interior, Exterior, Safety) and translates German terms to English.
- **Excel Output**: Generates formatted Excel files with conditional highlighting for missing data.
- **Modular Design**: Separate classes for Extract, Transform, and Load stages for easy maintenance.
- **Error Handling**: Robust error handling in extraction and loading phases.

## 🛠 Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-username/python-pdf-etl-automation.git
   cd python-pdf-etl-automation
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

   **Note**: Ensure you have Python 3.8+ installed. For Camelot, you may need additional system dependencies (e.g., Ghostscript for PDF processing).

## 🚀 Usage

### Basic Usage

1. Place your PDF file in the `pdf/` directory (e.g., `Serie Ibiza-1-1-3.pdf`).
2. Run the main script:
   ```bash
   python main.py
   ```
3. Check the output in `excel/output.xlsx`.

### Code Example

```python
from ingestion.extract import Extract
from ingestion.transform import Transform
from ingestion.load import Load
import os

# Define paths
PDF_PATH = os.path.join("pdf", "Serie Ibiza-1-1-3.pdf")
OUTPUT_PATH = os.path.join("excel", "output.xlsx")

# Extract data
extractor = Extract(PDF_PATH)
tables_df = extractor.extract_tables()
features = extractor.extract_features()

# Transform data
transformer = Transform(tables_df, features)
final_df = transformer.run()

# Load to Excel
loader = Load(final_df, OUTPUT_PATH)
loader.to_excel()
```

### Customization

- Modify `PDF_PATH` and `OUTPUT_PATH` in `main.py` for different files.
- Adjust transformation logic in `ingestion/transform.py` for other data sources.
- Update feature mappings or translations in the `Transform` class.

## 📁 Project Structure

```
python-automation/
├── main.py                 # Main script orchestrating the ETL pipeline
├── requirements.txt        # Python dependencies
├── README.md               # Project documentation
├── ingestion/              # ETL modules
│   ├── extract.py          # Data extraction from PDF
│   ├── transform.py        # Data transformation and processing
│   └── load.py             # Data loading to Excel
├── pdf/                    # Input PDF files
│   └── Serie Ibiza-1-1-3.pdf
├── excel/                  # Output Excel files
│   ├── output.xlsx
│   └── Serie Ibiza SK 1.12.25-2.xls
└── .gitignore              # Git ignore file
```

## 📦 Dependencies

- **pdfplumber**: For extracting text and features from PDFs.
- **camelot-py[cv]**: For table extraction from PDFs (includes OpenCV for image processing).
- **pandas**: Data manipulation and analysis.
- **openpyxl**: Reading/writing Excel files.
- **xlsxwriter**: Advanced Excel formatting.
- **numpy**: Numerical operations.

See `requirements.txt` for exact versions.

## ▶️ How to Run

1. Ensure your PDF is in the `pdf/` directory.
2. Execute the script:
   ```bash
   python main.py
   ```
3. The processed Excel file will be saved to `excel/output.xlsx`.
4. Open the Excel file to view the structured data with conditional formatting (missing values highlighted in red).

## 📊 Output Description

The output Excel file (`output.xlsx`) contains:

- **Columns**: Engine, Transmission, Power (kW/PS), Price, Feature, Included, Category, etc.
- **Rows**: Each row represents a vehicle variant with its associated features.
- **Formatting**:
  - Missing values ("N/A" or "( not specified )") are highlighted in red.
  - Features are categorized (Interior, Exterior, Safety, etc.).
  - German terms are translated to English where applicable.

Example output structure:

| Engine | Transmission | Power (kW/PS) | Price | Feature | Included | Category |
|--------|--------------|---------------|-------|---------|----------|----------|
| 1.0 TSI | Manual | 70/95 | €15,000 | Air Conditioning | Yes | Interior |
| 1.0 TSI | Manual | 70/95 | €15,000 | Parking Assistance |  | Safety |


## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

*Built with ❤️ for efficient PDF data processing.*
