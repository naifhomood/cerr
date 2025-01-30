import pandas as pd
from pathlib import Path

# قراءة ملف Excel
excel_file = Path(__file__).parent / 'data' / 'certificates.xlsx'
df = pd.read_excel(excel_file, engine='openpyxl')

# طباعة أسماء الأعمدة
print("\nأسماء الأعمدة:")
print("-" * 50)
for col in df.columns:
    print(col)

# طباعة أول صف كامل
print("\nأول صف في الملف:")
print("-" * 50)
first_row = df.iloc[0]
for col, value in first_row.items():
    print(f"{col}: {value}")

# طباعة الصفوف التي تحتوي على شهادات
print("\nالصفوف التي تحتوي على شهادات:")
print("-" * 50)
has_cert = df[df['Column1.employee_courses_degree.certificate_name'].notna()]
for _, row in has_cert.iterrows():
    print(f"الاسم: {row['Column1.employee_name']}")
    print(f"الشهادة: {row['Column1.employee_courses_degree.certificate_name']}")
    print(f"التاريخ: {row['Column1.employee_courses_degree.certificate_date']}")
    print(f"المرفق: {row['Column1.employee_courses_degree.attach_the_certificate']}")
    print("-" * 30)
