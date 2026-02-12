import pandas as pd
import re

def final_verify():
    excel_path = "excel/output.xlsx"
    df = pd.read_excel(excel_path)
    
    # 1. Check for known noise rows
    noise_words = {"und", "auf", "oder", "mit", "von", "aus"}
    features = df['name'].tolist()
    
    found_noise = []
    for f in features:
        if str(f).lower().strip() in noise_words:
            found_noise.append(f)
            
    # 2. Check for trailing dashes or CID artifacts
    trailing_artifacts = []
    for f in features:
        if re.search(r'[\-–—\.]\s*$', str(f)) or "(cid:" in str(f):
            trailing_artifacts.append(f)
            
    # 3. Check for split characters (multi-space)
    split_words = []
    for f in features:
        if re.search(r'\b[a-zA-Z]\s+[a-zA-Z]\b', str(f)):
            split_words.append(f)

    print(f"Total features: {len(features)}")
    print(f"Noise rows found: {len(found_noise)} {found_noise}")
    print(f"Trailing artifacts found: {len(trailing_artifacts)} {trailing_artifacts}")
    print(f"Split characters found: {len(split_words)} {split_words}")
    
    if not found_noise and not trailing_artifacts and not split_words:
        print("\nSUCCESS: Output is 100% clean and logical.")
    else:
        print("\nWARNING: Some issues may remain.")

if __name__ == "__main__":
    final_verify()
