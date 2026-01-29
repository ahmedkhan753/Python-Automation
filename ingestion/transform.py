import pandas as pd
import numpy as np
import re


class Transform:
    def __init__(self, table_df: pd.DataFrame, features: list[str]):
        self.table_df = table_df
        self.features = features
        self.feature_df = None
        self.final_df = None

    # 1️ CLEAN RAW TABLE DATA
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

        df = df[~df.apply(is_noise, axis=1)]

        self.table_df = df.reset_index(drop=True)

    # 2️ NORMALIZE COLUMN NAMES
    def normalize_data(self):
        df = self.table_df.copy()

        COLUMN_MAP = {
            "Motor": "Engine",
            "Getriebe": "Transmission",
            "Leistung  (kW/PS)": "Power (kW/PS)",
            "Listenpreis1": "Price",
        }

        df.rename(columns=COLUMN_MAP, inplace=True)

        self.table_df = df

    # 3️ CLEAN & NORMALIZE FEATURE TEXT
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

    # 4️ BULLET / SYMBOL → LOGIC
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

    # 5️ KEYWORD → CATEGORY MAPPING
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

    # 6️ GERMAN → ENGLISH TRANSLATION 
    def translate_features(self):
        TRANSLATION_MAP = {
            "Multifunktionslenkrad": "Multifunction Steering Wheel",
            "Klimaanlage": "Air Conditioning",
            "Einparkhilfe": "Parking Assistance",
            "Rückfahrkamera": "Rear View Camera",
            "Scheinwerfer": "Headlights",
            "Airbag": "Airbag",
            "Regensensor": "Rain Sensor",
            "Zentralverriegelung": "Central Locking",
        }

        def translate(text: str) -> str:
            for de, en in TRANSLATION_MAP.items():
                text = re.sub(de, en, text, flags=re.IGNORECASE)
            return text

        self.feature_df["Feature"] = self.feature_df["Feature"].apply(translate)

    # 7️ FINAL DATA MODEL
    def final_data_model(self):
        table_df = self.table_df.copy()
        feature_df = self.feature_df.copy()

        # Cartesian join: features apply to all variants
        table_df["key"] = 1
        feature_df["key"] = 1

        self.final_df = (
            pd.merge(table_df, feature_df, on="key")
            .drop(columns="key")
            .reset_index(drop=True)
        )

    # 8️ VALIDATION (DO NOT FIX DATA)
    def validate_data(self):
        return self.final_df

    #  RUN PIPELINE
    def run(self) -> pd.DataFrame:
        self.clean_data()
        self.normalize_data()
        self.symbol_to_logic()
        self.keyword_mapping()
        self.translate_features()   
        self.final_data_model()
        return self.validate_data()
