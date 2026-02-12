import pandas as pd
from ingestion.transform import Transform

def test_cleaning():
    print("Testing Transform.normalize_feature_text...")
    
    # Mock data for Transform init
    mock_df = pd.DataFrame()
    mock_features = []
    transformer = Transform(mock_df, mock_features)
    
    test_cases = [
        # 1. Trailing dash with CID artifact
        ("Manuelle Klimaanlage mit Pollen- und Staubfilter - (cid:127)", "Manuelle Klimaanlage mit Pollen- und Staubfilter"),
        ("( für Motoren über 100.000 km) - (cid:127)", "( für Motoren über 100.000 km)"),
        
        # 2. Multiple trailing symbols
        ("Feature Name - .  ", "Feature Name"),
        
        # 3. CID in middle
        ("Some (cid:127) Feature", "Some Feature"),
        
        # 4. Bullet removal
        ("• Black Feature", "Black Feature"),
        
        # 5. Spacing fixes (multi-space)
        ("T SI Engine", "TSI Engine"),
        ("K l i m a a n l a g e", "Klimaanlage"),
        ("v o r n", "vorn"),
    ]
    
    passed = 0
    for input_text, expected_output in test_cases:
        actual_output = transformer.normalize_feature_text(input_text)
        if actual_output == expected_output:
            print(f"✅ PASS: '{input_text}' -> '{actual_output}'")
            passed += 1
        else:
            print(f"❌ FAIL: '{input_text}'")
            print(f"   Expected: '{expected_output}'")
            print(f"   Actual:   '{actual_output}'")
            
    print(f"\nPassed {passed}/{len(test_cases)} cases.")
    
    if passed == len(test_cases):
        print("\nAll unit tests PASSED!")
    else:
        print("\nSome tests FAILED.")

if __name__ == "__main__":
    test_cleaning()
