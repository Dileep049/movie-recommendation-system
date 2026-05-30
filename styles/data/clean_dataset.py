import pandas as pd
import re
import os

# Base directory setup
base_dir = os.path.dirname(os.path.abspath(__file__)) if '__file__' in locals() else "."
# CODE LO LINE 7 DEENINI:
file_path = os.path.join(base_dir, "data", "telugu_movies_10000.csv")

# ILA REPI PIRE MAARCHANDI (data ane extra word tecchesam):
file_path = os.path.join(base_dir, "telugu_movies_10000.csv")

print("Cleaning process start ayyindi...")

# 1. Load the original dataset
if os.path.exists(file_path):
    df = pd.read_csv(file_path)

    # 2. Removes trailing space and numbers (e.g., Baahubali 1 -> Baahubali)
    df['title'] = df['title'].astype(str).str.replace(r'\s*\d+$', '', regex=True)

    # 3. Overwrite back to CSV
    df.to_csv(file_path, index=False)
    print("✅ CSV File successfully update ayyindi! Titles nundi numbers permanently remove aipoyayi.")
else:
    print(f"❌ Error: File ikkada ledu -> {file_path}")