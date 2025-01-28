import pandas as pd
import json
import os
from datetime import datetime

def convert_excel_to_json():
    """Convert Excel file to JSON."""
    try:
        excel_path = os.path.join('data', 'certificates.xlsx')
        if not os.path.exists(excel_path):
            print(f"Error: Excel file not found at: {excel_path}")
            return
        
        # Read the file
        df = pd.read_excel(excel_path, keep_default_na=False)
        print(f"Read {len(df)} records from Excel")
        
        # Convert DataFrame to list of dictionaries
        certificates = df.to_dict('records')
        
        # Process dates and missing values
        for cert in certificates:
            # Handle dates
            date_fields = [
                'Column1.employee_courses_degree.certificate_date',
                'Column1.date_of_joining'
            ]
            
            for field in date_fields:
                if field in cert:
                    if pd.notnull(cert[field]):
                        if isinstance(cert[field], datetime):
                            cert[field] = cert[field].strftime('%Y-%m-%d')
                    else:
                        cert[field] = None
            
            # Handle URLs
            url_fields = [
                'Column1.employee_courses_degree.attach_the_certificate',
                'urlnext',
                'certificate url'
            ]
            for field in url_fields:
                if field in cert and pd.isnull(cert[field]):
                    cert[field] = ""
        
        # Save to JSON file
        json_path = os.path.join('data', 'certificates.json')
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(certificates, f, ensure_ascii=False, indent=2)
        
        print(f"Successfully saved JSON file to: {json_path}")
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == '__main__':
    convert_excel_to_json()
