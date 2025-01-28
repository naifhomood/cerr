import pandas as pd
import json

def clean_data(value):
    """تنظيف قيمة البيانات"""
    if pd.isna(value) or value == '' or value == 'nan':
        return None
    if isinstance(value, str):
        value = value.strip()
        if value == '':
            return None
    if isinstance(value, pd.Timestamp):
        return value.strftime('%Y-%m-%d')
    return value

# قراءة ملف Excel
df = pd.read_excel('data/certificates.xlsx', keep_default_na=False)

# تحويل البيانات
certificates = []
for _, row in df.iterrows():
    cert = {
        'Column1.name': clean_data(row['Column1.name']),
        'Column1.department': clean_data(row['Column1.department']),
        'Column1.employee_name': clean_data(row['Column1.employee_name']),
        'Column1.employee_courses_degree.certificate_name': clean_data(row['Column1.employee_courses_degree.certificate_name']),
        'Column1.employee_courses_degree.certificate_date': clean_data(row['Column1.employee_courses_degree.certificate_date']),
        'Column1.employee_courses_degree.attach_the_certificate': clean_data(row['Column1.employee_courses_degree.attach_the_certificate']),
        'Column1.gender': clean_data(row['Column1.gender']),
        'Column1.date_of_joining': clean_data(row['Column1.date_of_joining']),
        'Column1.designation': clean_data(row['Column1.designation']),
        'Column1.branch': clean_data(row['Column1.branch']),
        'urlnext': 'https://next.rajhifoundation.org',
        'certificate url': None
    }
    if cert['Column1.name']:
        certificates.append(cert)

# حفظ إلى ملف JSON
with open('data/certificates.json', 'w', encoding='utf-8') as f:
    json.dump(certificates, f, ensure_ascii=False, indent=2)

print(f'تم تحويل {len(certificates)} سجل إلى JSON')
