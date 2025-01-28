import subprocess
import time
import os
import hashlib
from datetime import datetime
import logging
import pandas as pd
import json

# إعداد التسجيل
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    handlers=[
        logging.FileHandler('auto_sync.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

def convert_excel_to_json():
    """تحويل ملف Excel إلى JSON"""
    try:
        excel_path = os.path.join('data', 'certificates.xlsx')
        df = pd.read_excel(excel_path, keep_default_na=False)
        logging.info(f"تم قراءة {len(df)} سجل من Excel")
        
        # تحويل DataFrame إلى قائمة
        certificates = df.to_dict('records')
        
        # معالجة التواريخ والقيم الفارغة
        for cert in certificates:
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
                if field in cert and pd.isnull(cert[field]):
                    cert[field] = ""
        
        # حفظ إلى ملف JSON
        json_path = os.path.join('data', 'certificates.json')
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(certificates, f, ensure_ascii=False, indent=2)
        
        logging.info(f"تم حفظ الملف بنجاح في: {json_path}")
        return True
        
    except Exception as e:
        logging.error(f"خطأ في تحويل الملف: {str(e)}")
        return False

def get_file_hash(filepath):
    """حساب قيمة التجزئة للملف"""
    max_retries = 3
    retry_delay = 2
    
    for attempt in range(max_retries):
        try:
            with open(filepath, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except PermissionError:
            if attempt < max_retries - 1:
                logging.warning(f'الملف مفتوح، محاولة مرة أخرى بعد {retry_delay} ثوانٍ...')
                time.sleep(retry_delay)
            else:
                logging.error('لا يمكن الوصول إلى الملف بعد عدة محاولات')
                return None

def run_git_commands():
    """تنفيذ أوامر Git"""
    try:
        # تهيئة Git إذا لم يكن مهيأ
        subprocess.run(['git', 'config', '--global', 'user.email', 'naifhomood@gmail.com'], check=True)
        subprocess.run(['git', 'config', '--global', 'user.name', 'naifhomood'], check=True)
        
        # تحويل Excel إلى JSON
        if not convert_excel_to_json():
            logging.error('فشل في تحويل الملف إلى JSON')
            return False
            
        # محاولات إعادة الدفع
        max_retries = 3
        retry_delay = 60  # ثانية واحدة
        
        for attempt in range(max_retries):
            try:
                # تهيئة أوامر Git
                commands = [
                    ['git', 'add', 'data/certificates.xlsx', 'data/certificates.json'],
                    ['git', 'commit', '-m', f'تحديث تلقائي للبيانات - {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'],
                    ['git', 'pull', '--rebase', 'origin', 'main'],  # سحب التغييرات أولاً
                    ['git', 'push', 'origin', 'main']
                ]
                
                # تنفيذ كل أمر
                for cmd in commands:
                    result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
                    if result.returncode != 0 and 'nothing to commit' not in result.stderr:
                        logging.error(f'خطأ في تنفيذ الأمر {cmd}: {result.stderr}')
                        raise Exception(f'فشل في تنفيذ الأمر: {cmd}')
                    logging.info(f'تم تنفيذ الأمر {cmd[0]} {cmd[1]} بنجاح')
                
                return True
                
            except Exception as e:
                if attempt < max_retries - 1:
                    logging.warning(f'فشلت المحاولة {attempt + 1} من {max_retries}. إعادة المحاولة بعد {retry_delay} ثانية...')
                    time.sleep(retry_delay)
                    retry_delay *= 2  # مضاعفة وقت الانتظار في كل مرة
                else:
                    logging.error(f'فشلت جميع المحاولات: {str(e)}')
                    return False
                    
    except Exception as e:
        logging.error(f'حدث خطأ أثناء تنفيذ أوامر Git: {str(e)}')
        return False

def monitor_excel_file():
    """مراقبة ملف Excel للتغييرات"""
    excel_path = os.path.join('data', 'certificates.xlsx')
    
    if not os.path.exists(excel_path):
        logging.error(f'ملف Excel غير موجود في المسار: {excel_path}')
        return
    
    last_hash = get_file_hash(excel_path)
    logging.info('بدء مراقبة ملف Excel للتغييرات...')
    
    while True:
        try:
            current_hash = get_file_hash(excel_path)
            
            if current_hash != last_hash:
                logging.info('تم اكتشاف تغييرات في ملف Excel')
                
                # انتظر قليلاً للتأكد من اكتمال عملية الحفظ
                time.sleep(10)  # زيادة وقت الانتظار
                
                # تنفيذ أوامر Git
                if run_git_commands():
                    logging.info('تم رفع التغييرات بنجاح')
                    last_hash = current_hash
                else:
                    logging.error('فشل في رفع التغييرات')
            
            # انتظار قبل الفحص التالي
            time.sleep(30)  # زيادة الفترة بين عمليات الفحص
            
        except Exception as e:
            logging.error(f'حدث خطأ: {str(e)}')
            time.sleep(60)

if __name__ == '__main__':
    monitor_excel_file()
