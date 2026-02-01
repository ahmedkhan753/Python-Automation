import pandas as pd
import numpy as np
import re


class Transform:
    def __init__(self, table_df: pd.DataFrame, features: list[str]):
        self.table_df = table_df
        self.features = features
        self.feature_df = None
        self.final_df = None

    # 1️⃣ CLEAN RAW TABLE DATA
    def clean_data(self):
        df = self.table_df.copy()
        # Replace empty strings with NaN
        df.replace("", np.nan, inplace=True)
        # Drop fully empty rows
        df.dropna(how="all", inplace=True)
        # Strip whitespace (Pandas 2.x safe)
        df = df.apply(
            lambda col: col.str.strip() if col.dtype == "object" else col
        )
        # Remove obvious header / footer noise
        noise_patterns = [
            "Preisliste",
            "www.seat",
            "Gültig ab",
            "Nun muss der Defekt",
            r"\(cid:",
        ]

        def is_noise(row):
            row_text = " ".join(row.fillna("").astype(str).tolist())
            return any(re.search(p, row_text, re.IGNORECASE) for p in noise_patterns)

        # Find header row
        header_idx = None
        for i, row in df.iterrows():
            row_str = " ".join(row.fillna("").astype(str).tolist())
            if "Motor" in row_str and "Getriebe" in row_str:
                header_idx = i
                break
        if header_idx is not None:
            # Set header
            df.columns = df.iloc[header_idx]
            # Drop rows including and before header
            df = df.iloc[header_idx + 1:]
        else:
            print("Warning: Header not found! Using default columns.")
        self.table_df = df.reset_index(drop=True)

    def normalize_data(self):
        # We don't want to translate column names anymore, but we'll keep the method for future normalization if needed.
        pass

    # 3️⃣ CLEAN & NORMALIZE FEATURE TEXT
    def normalize_feature_text(self, text: str) -> str:
        # Fix broken words caused by PDF spacing
        fixes = {
            r"\bB\s+eifahrer\b": "Beifahrer",
            r"\bm\s+it\b": "mit",
            r"\bT\s+SI\b": "TSI",
            r"\bA\s+ssist\b": "Assist",
        }
        for pattern, replacement in fixes.items():
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        # Remove multiple spaces
        text = re.sub(r"\s{2,}", " ", text)
        return text.strip()

    # 4️⃣ BULLET / SYMBOL → LOGIC
    def symbol_to_logic(self):
        rows = []
        for line in self.features:
            if not line or len(line.strip()) < 5:
                continue
            has_feature = any(b in line for b in ["•", "▪", "●"])
            clean_text = (
                line.replace("•", "")
                .replace("▪", "")
                .replace("●", "")
                .strip()
            )
            clean_text = self.normalize_feature_text(clean_text)
            rows.append({
                "Feature": clean_text,
                "Included": "Yes" if has_feature else ""
            })
        self.feature_df = pd.DataFrame(rows)

    # 5️⃣ KEYWORD → CATEGORY MAPPING
    def keyword_mapping(self):
        KEYWORD_CATEGORY_MAP = {
            "lenkrad": "Interior",
            "cockpit": "Interior",
            "klimaanlage": "Interior",
            "sitz": "Interior",
            "scheinwerfer": "Exterior",
            "led": "Exterior",
            "felgen": "Exterior",
            "airbag": "Safety",
            "assist": "Safety",
            "kamera": "Safety",
            "brems": "Safety",
        }

        def map_category(feature: str) -> str:
            for keyword, category in KEYWORD_CATEGORY_MAP.items():
                if keyword in feature.lower():
                    return category
            return "Uncategorized"

        self.feature_df["Category"] = self.feature_df["Feature"].apply(map_category)


    # 7️⃣ FINAL DATA MODEL
    def final_data_model(self):
        table_df = self.table_df.copy()
        feature_df = self.feature_df.copy()
        # Cartesian join: features apply to all variants
        table_df["key"] = 1
        feature_df["key"] = 1
        merged_df = (
            pd.merge(table_df, feature_df, on="key")
            .drop(columns="key")
            .reset_index(drop=True)
            .fillna("N/A")
        )
        # Remove columns that are entirely NaN or empty
        merged_df = merged_df.dropna(axis=1, how='all')
        # Remove columns with no useful values (e.g., all 'N/A' or empty strings)
        useful_columns = []
        for col in merged_df.columns:
            if pd.isna(col):
                continue
            if (
                merged_df[col].notna().any()
                and not (merged_df[col] == 'N/A').all()
                and not (merged_df[col] == '').all()
            ):
                useful_columns.append(col)
        self.final_df = merged_df[useful_columns]

    # 8️⃣ VALIDATION (DO NOT FIX DATA)
    def validate_data(self):
        return self.final_df

    # RUN PIPELINE
    def run(self) -> pd.DataFrame:
        self.clean_data()
        self.normalize_data()
        self.symbol_to_logic()
        self.keyword_mapping()
        self.final_data_model()
        return self.validate_data()
