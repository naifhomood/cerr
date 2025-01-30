import pandas as pd
import json
from pathlib import Path
import os
import time

def clean_text(text):
    if pd.isna(text):
        return ""
    return str(text).strip()

def format_date(date):
    if pd.isna(date):
        return ""
    try:
        return pd.to_datetime(date).strftime('%Y-%m-%d')
    except:
        return str(date).strip()

def update_json():
    try:
        # تحديد المسارات
        base_dir = Path(__file__).parent
        excel_file = base_dir / 'data' / 'certificates.xlsx'
        json_file = base_dir / 'data' / 'certificates.json'
        
        print(f"قراءة الملف: {excel_file}")
        
        # قراءة ملف Excel
        df = pd.read_excel(excel_file, engine='openpyxl')
        print(f"تم قراءة {len(df)} سجل")
        
        # تنظيف البيانات
        df = df.fillna('')
        
        # تحويل إلى JSON
        data = []
        for _, row in df.iterrows():
            cert_name = clean_text(row['Column1.employee_courses_degree.certificate_name'])
            cert_date = format_date(row['Column1.employee_courses_degree.certificate_date'])
            cert_path = clean_text(row['Column1.employee_courses_degree.attach_the_certificate'])
            
            entry = {
                'name': clean_text(row['Column1.name']),
                'department': clean_text(row['Column1.department']),
                'employee_name': clean_text(row['Column1.employee_name']),
                'employee_courses_degree': {
                    'certificate_name': cert_name,
                    'certificate_date': cert_date,
                    'attach_the_certificate': cert_path
                },
                'user_id': clean_text(row['Column1.user_id']),
                'gender': clean_text(row['Column1.gender']),
                'date_of_joining': format_date(row['Column1.date_of_joining']),
                'designation': clean_text(row.get('Column1.designation', '')),
                'branch': clean_text(row.get('Column1.branch', '')),
                'urlnext': 'https://next.rajhifoundation.org',
                'certificate_url': f"https://next.rajhifoundation.org{cert_path}" if cert_path else ''
            }
            
            data.append(entry)
        
        # حفظ الملف
        print(f"\nحفظ إلى: {json_file}")
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print("✅ تم التحديث بنجاح")
        
        # تنفيذ أوامر Git
        os.system('git add data/certificates.json')
        os.system(f'git commit -m "تحديث بنية البيانات وإصلاح التنسيق - {time.strftime("%Y-%m-%d %H:%M:%S")}"')
        os.system('git pull --rebase origin main')
        os.system('git push origin main')
        
        return True
    except Exception as e:
        print(f"❌ خطأ: {str(e)}")
        return False

if __name__ == '__main__':
    update_json()
