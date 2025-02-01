from flask import Flask, render_template, jsonify
import json
import os
import logging

app = Flask(__name__)

# إعداد التسجيل
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def load_certificates():
    """تحميل الشهادات من ملف JSON."""
    try:
        json_path = os.path.join('data', 'certificates.json')
        if not os.path.exists(json_path):
            logger.error(f"ملف JSON غير موجود في المسار: {json_path}")
            return []
        
        # قراءة الملف JSON
        with open(json_path, 'r', encoding='utf-8') as f:
            certificates = json.load(f)
            
        logger.info(f"تم قراءة {len(certificates)} سجل من ملف JSON")
        return certificates
    
    except Exception as e:
        logger.error(f"خطأ في تحميل ملف JSON: {str(e)}")
        return []

@app.route('/')
def index():
    """عرض الصفحة الرئيسية."""
    return render_template('index.html')

@app.route('/api/certificates')
def get_certificates():
    """نقطة نهاية API للحصول على بيانات الشهادات."""
    certificates = load_certificates()
    return jsonify(certificates)

if __name__ == '__main__':
    app.run(debug=True, port=5003)
