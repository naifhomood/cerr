import time
import os
import hashlib
import subprocess
from datetime import datetime
import logging

# إعداد التسجيل
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    handlers=[
        logging.FileHandler('auto_sync.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

def get_file_hash(filepath):
    """حساب قيمة التجزئة للملف"""
    with open(filepath, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()

def run_git_commands():
    """تنفيذ أوامر Git"""
    try:
        # تهيئة أوامر Git
        commands = [
            ['git', 'add', 'data/certificates.xlsx'],
            ['git', 'commit', '-m', f'تحديث تلقائي للبيانات - {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'],
            ['git', 'push', 'origin', 'main']
        ]
        
        # تنفيذ كل أمر
        for cmd in commands:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0 and 'nothing to commit' not in result.stderr:
                logging.error(f'خطأ في تنفيذ الأمر {cmd}: {result.stderr}')
                return False
        return True
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
                time.sleep(5)
                
                # تنفيذ أوامر Git
                if run_git_commands():
                    logging.info('تم رفع التغييرات بنجاح')
                    last_hash = current_hash
                else:
                    logging.error('فشل في رفع التغييرات')
            
            # انتظار قبل الفحص التالي
            time.sleep(10)
            
        except Exception as e:
            logging.error(f'حدث خطأ: {str(e)}')
            time.sleep(30)

if __name__ == '__main__':
    monitor_excel_file()
