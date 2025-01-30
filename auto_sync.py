import os
import time
import logging
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# إعداد التسجيل
logging.basicConfig(
    filename='auto_sync.log',
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    encoding='utf-8'
)

def run_git_commands():
    """تنفيذ أوامر Git"""
    try:
        # إضافة الملفات
        subprocess.run(['git', 'add', 'data/certificates.xlsx'], check=True)
        subprocess.run(['git', 'add', 'data/certificates.json'], check=True)
        
        # عمل commit
        subprocess.run(['git', 'commit', '-m', 'تحديث البيانات'], check=True)
        
        # رفع التغييرات
        subprocess.run(['git', 'push', 'origin', 'main'], check=True)
        
        logging.info('تم رفع التغييرات بنجاح')
    except subprocess.CalledProcessError as e:
        logging.error(f'خطأ في تنفيذ الأمر {e.cmd}: {e.output}')
        logging.info('فشل في رفع التغييرات')

class FileChangeHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path.endswith('certificates.xlsx'):
            logging.info('تم اكتشاف تغييرات في ملف Excel')
            try:
                # تشغيل سكريبت التحويل
                subprocess.run(['python', 'convert.py'], check=True)
                # رفع التغييرات
                run_git_commands()
            except subprocess.CalledProcessError as e:
                logging.error(f'خطأ في تنفيذ الأمر: {e}')

if __name__ == "__main__":
    # إنشاء المراقب
    event_handler = FileChangeHandler()
    observer = Observer()
    observer.schedule(event_handler, path='data', recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
