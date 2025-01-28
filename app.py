from flask import Flask, render_template, jsonify
import pandas as pd
import os
from datetime import datetime
import logging

app = Flask(__name__)

# إعداد التسجيل
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def load_certificates():
    """Load certificates from Excel file."""
    try:
        excel_path = os.path.join('data', 'certificates.xlsx')
        if not os.path.exists(excel_path):
            logger.error(f"ملف Excel غير موجود في المسار: {excel_path}")
            return []
        
        # قراءة الملف مع معالجة القيم المفقودة
        df = pd.read_excel(excel_path, keep_default_na=False)
        logger.info(f"تم قراءة {len(df)} سجل من ملف Excel")
        logger.debug(f"أسماء الأعمدة: {df.columns.tolist()}")
        
        # تحويل DataFrame إلى قائمة
        certificates = df.to_dict('records')
        
        # معالجة التواريخ والقيم المفقودة
        for cert in certificates:
            try:
                # معالجة التواريخ
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
                
                # معالجة الروابط
                url_fields = [
                    'Column1.employee_courses_degree.attach_the_certificate',
                    'urlnext',
                    'certificate url'
                ]
                
                for field in url_fields:
                    if field in cert:
                        if pd.isna(cert[field]) or cert[field] == '':
                            cert[field] = None
                
                # معالجة باقي الحقول النصية
                for key in cert:
                    if key not in date_fields + url_fields:
                        if pd.isna(cert[key]) or cert[key] == '':
                            cert[key] = None
                        else:
                            cert[key] = str(cert[key])
            
            except Exception as e:
                logger.error(f"خطأ في معالجة السجل: {cert}")
                logger.error(f"تفاصيل الخطأ: {str(e)}")
        
        return certificates
    
    except Exception as e:
        logger.error(f"خطأ في تحميل ملف Excel: {str(e)}")
        return []

@app.route('/')
def index():
    """Render main page."""
    return render_template('index.html')

@app.route('/api/certificates')
def get_certificates():
    """API endpoint to get certificates data."""
    certificates = load_certificates()
    return jsonify(certificates)

if __name__ == '__main__':
    app.run(debug=True, port=5003)
