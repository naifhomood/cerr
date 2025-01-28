import pandas as pd
import json

def clean_data(value):
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
        'name': clean_data(row['Column1.name']),
        'department': clean_data(row['Column1.department']),
        'employee_name': clean_data(row['Column1.employee_name']),
        'certificate_name': clean_data(row['Column1.employee_courses_degree.certificate_name']),
        'certificate_date': clean_data(row['Column1.employee_courses_degree.certificate_date']),
        'certificate_url': clean_data(row['Column1.employee_courses_degree.attach_the_certificate']),
        'gender': clean_data(row['Column1.gender']),
        'date_of_joining': clean_data(row['Column1.date_of_joining']),
        'designation': clean_data(row['Column1.designation']),
        'branch': clean_data(row['Column1.branch'])
    }
    if cert['name']:
        certificates.append(cert)

# حفظ إلى ملف JSON
with open('data/certificates.json', 'w', encoding='utf-8') as f:
    json.dump(certificates, f, ensure_ascii=False, indent=2)

print(f'تم تحويل {len(certificates)} سجل إلى JSON')
