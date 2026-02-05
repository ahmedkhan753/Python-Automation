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
        """Fix broken words, spacing issues, and remove noise labels."""
        if not text:
            return ""

        # 1. Join single characters detached from words (e.g., "v orn", "a b", "F R", "1 5-Zoll")
        # Handle cases like "v orn", "h inten", "a b", "i n", "f ür"
        text = re.sub(r'\b([a-z])\s+(?=[a-z])', r'\1', text)
        
        # Handle specific uppercase/model detachments like "F R", "L ED"
        text = re.sub(r'\b([A-Z])\s+(?=[A-Z])', r'\1', text)
        
        # Handle number spacing in specs (e.g., "1 5-Zoll", "1 6-Zoll")
        text = re.sub(r'\b(\d)\s+(?=\d)', r'\1', text)

        # 2. Specific keyword fixes for German automotive context
        fixes = {
            r"\bRegensenso\b": "Regensensor",
            r"\bProduktion bis M ärz\b": "Produktion bis März",
            r"\bu\s+nd\b": "und",
            r"\ba\s+uf\b": "auf",
            r"\bT\s+SI\b": "TSI",
        }
        for pattern, replacement in fixes.items():
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)

        # 3. Remove trailing noise: dashes, double dashes, especially at the end
        # Remove patterns like "- -", "--", or lone "-" at the end of the string
        text = re.sub(r'\s*[-–—\s]+$', '', text)
        
        # 4. Remove internal double dashes often used as fillers in tables
        text = text.replace(" - -", "").replace(" --", "")

        # 5. Remove CID artifacts
        text = re.sub(r"\(cid:\d+\)", "", text)

        # 6. Remove leading bullets if they survived
        bullets = ["•", "▪", "●", "·"]
        for b in bullets:
            text = text.replace(b, "")

        # 7. Final cleanup: Remove multiple spaces
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
        if not rows:
            # Handle empty features case
            self.feature_df = pd.DataFrame(columns=["Feature", "Included"])
        else:
            self.feature_df = pd.DataFrame(rows)

    # 5️⃣ KEYWORD → CATEGORY MAPPING
    def keyword_mapping(self):
        KEYWORD_CATEGORY_MAP = {
            "airbag": "_Sicherheit",
            "assist": "_Sicherheit",
            "kamera": "_Sicherheit",
            "brems": "_Sicherheit",
            "stabilitäts": "_Sicherheit",
            "pannen": "_Sicherheit",
            "sicherheits": "_Sicherheit",
            "parkhilfe": "_Sicherheit",
            "spur": "_Sicherheit",
            "müdigkeit": "_Sicherheit",
            "felgen": "_Räder & Co",
            "reifen": "_Räder & Co",
            "rad": "_Räder & Co",
            "reifendruck": "_Räder & Co",
            "infotainment": "_Infotainment",
            "radio": "_Infotainment",
            "full link": "_Infotainment",
            "cockpit": "_Infotainment",
            "connect": "_Infotainment",
            "media": "_Infotainment",
            "bluetooth": "_Infotainment",
            "usb": "_Infotainment",
            "lautsprecher": "_Infotainment",
            "lenkrad": "_Innen",
            "klimaanlage": "_Innen",
            "sitz": "_Innen",
            "innenspiegel": "_Innen",
            "fensterheber": "_Innen",
            "schaltknauf": "_Innen",
            "dachhimmel": "_Innen",
            "mittelarmlehne": "_Innen",
            "komfort": "_Innen",
            "geschwindigkeits": "_Innen",
            "scheinwerfer": "_Außen",
            "led": "_Außen",
            "außenspiegel": "_Außen",
            "lackiert": "_Außen",
            "getönte": "_Außen",
            "nebelscheinwerfer": "_Außen",
            "heckleuchten": "_Außen",
            "stoßfänger": "_Außen",
        }

        def map_category(feature: str) -> str:
            for keyword, category in KEYWORD_CATEGORY_MAP.items():
                if keyword in feature.lower():
                    return category
            return "_Innen" # Default to _Innen as seen in many rows

        if self.feature_df.empty:
            self.feature_df["type"] = []
            self.feature_df["name"] = []
            return

        self.feature_df["type"] = self.feature_df["Feature"].apply(map_category)
        self.feature_df.rename(columns={"Feature": "name"}, inplace=True)


    # 7️⃣ FINAL DATA MODEL
    def final_data_model(self):
        feature_df = self.feature_df.copy()
        
        # Create the required columns with default values as per screenshot
        feature_df["online"] = 1
        feature_df["details"] = 1
        feature_df["code"] = 1
        feature_df["export_excel"] = 1
        feature_df["attribute"] = 1
        feature_df["FILTERABLE"] = 1
        feature_df["Style"] = 1
        feature_df["cat"] = 1
        feature_df["S"] = 1
        
        # Select and reorder columns
        target_cols = ["name", "type", "online", "details", "code", "export_excel", "attribute", "FILTERABLE", "Style", "cat", "S"]
        self.final_df = feature_df[target_cols]

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
