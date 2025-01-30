import pandas as pd
import json

# قراءة ملف Excel
excel_df = pd.read_excel('data/certificates.xlsx')

# قراءة ملف JSON
with open('data/certificates.json', 'r', encoding='utf-8') as f:
    json_data = json.load(f)

print(f'عدد السجلات في Excel: {len(excel_df)}')
print(f'عدد السجلات في JSON: {len(json_data)}')

# تحويل البيانات إلى مجموعات للمقارنة
excel_ids = set(excel_df['Column1.name'].tolist())
json_ids = set(item.get('Column1.name', '') for item in json_data)

# إيجاد الفروق
missing_in_json = excel_ids - json_ids
extra_in_json = json_ids - excel_ids

print('\nالسجلات الموجودة في Excel ولكن غير موجودة في JSON:')
for id in missing_in_json:
    print(f'- {id}')

print('\nالسجلات الموجودة في JSON ولكن غير موجودة في Excel:')
for id in extra_in_json:
    print(f'- {id}')
