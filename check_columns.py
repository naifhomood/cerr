import pandas as pd
from pathlib import Path

# قراءة الملف
excel_file = Path(__file__).parent / 'data' / 'certificates.xlsx'
df = pd.read_excel(excel_file, engine='openpyxl')

# طباعة أسماء الأعمدة
print("أسماء الأعمدة في الملف:")
for col in df.columns:
    print(f"- {col}")
