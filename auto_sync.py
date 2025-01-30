import os
import time
import logging
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from pathlib import Path
import shutil

# إعداد التسجيل
logging.basicConfig(
    filename='auto_sync.log',
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    encoding='utf-8'
)

def check_and_remove_lock_files():
    """التحقق من وجود ملفات القفل وإزالتها إذا كانت قديمة"""
    git_dir = Path('.git')
    lock_files = [
        git_dir / 'index.lock',
        git_dir / '.MERGE_MSG.swp',
        git_dir / 'MERGE_HEAD'
    ]
    
    for lock_file in lock_files:
        if lock_file.exists():
            try:
                # التحقق من عمر الملف
                file_age = time.time() - lock_file.stat().st_mtime
                if file_age > 300:  # 5 دقائق
                    lock_file.unlink()
                    logging.info(f'تم حذف ملف القفل القديم: {lock_file}')
            except Exception as e:
                logging.error(f'خطأ في حذف ملف القفل: {e}')

def wait_for_file_access(file_path, timeout=60):
    """الانتظار حتى يكون الملف متاحاً للوصول"""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            with open(file_path, 'rb') as f:
                return True
        except PermissionError:
            time.sleep(1)
    return False

def run_git_command(command, retries=3, delay=5):
    """تنفيذ أمر Git مع إعادة المحاولة"""
    for attempt in range(retries):
        try:
            check_and_remove_lock_files()
            result = subprocess.run(command, check=True, capture_output=True, text=True)
            logging.info(f'تم تنفيذ الأمر {command[0]} بنجاح')
            return True
        except subprocess.CalledProcessError as e:
            logging.error(f'خطأ في تنفيذ الأمر {command}: {e.stderr}')
            if attempt < retries - 1:
                logging.info(f'فشلت المحاولة {attempt + 1} من {retries}. إعادة المحاولة بعد {delay} ثانية...')
                time.sleep(delay)
                delay *= 2  # مضاعفة وقت الانتظار مع كل محاولة
            else:
                logging.error('فشلت جميع المحاولات')
                return False
        except Exception as e:
            logging.error(f'خطأ غير متوقع: {e}')
            return False

def run_git_commands():
    """تنفيذ أوامر Git"""
    try:
        # التأكد من عدم وجود تغييرات غير مرحلة
        run_git_command(['git', 'stash'])
        
        # تحديث من المستودع البعيد
        run_git_command(['git', 'fetch', 'origin'])
        run_git_command(['git', 'pull', '--rebase', 'origin', 'main'])
        
        # إضافة الملفات
        if run_git_command(['git', 'add', 'data/certificates.xlsx']) and \
           run_git_command(['git', 'add', 'data/certificates.json']):
            
            # عمل commit
            commit_msg = f'تحديث تلقائي للبيانات - {time.strftime("%Y-%m-%d %H:%M:%S")}'
            if run_git_command(['git', 'commit', '-m', commit_msg]):
                
                # رفع التغييرات
                if run_git_command(['git', 'push', 'origin', 'main']):
                    logging.info('تم رفع التغييرات بنجاح')
                    return True
        
        logging.error('فشل في رفع التغييرات')
        return False
    except Exception as e:
        logging.error(f'حدث خطأ أثناء تنفيذ أوامر Git: {e}')
        return False

class FileChangeHandler(FileSystemEventHandler):
    def __init__(self):
        self.last_modified = 0
        self.cooldown = 5  # فترة الانتظار بين التحديثات (بالثواني)

    def on_modified(self, event):
        if event.src_path.endswith('certificates.xlsx'):
            current_time = time.time()
            if current_time - self.last_modified < self.cooldown:
                return
            
            self.last_modified = current_time
            logging.info('تم اكتشاف تغييرات في ملف Excel')
            
            # انتظار حتى يكون الملف متاحاً
            if not wait_for_file_access(event.src_path):
                logging.error('تعذر الوصول إلى الملف - تخطي هذا التحديث')
                return
                
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
