import os
import time
import logging
import pandas as pd
import json
import win32serviceutil
import win32service
import win32event
import servicemanager
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import sys
import subprocess

# إعداد التسجيل
logging.basicConfig(
    filename='auto_sync.log',
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    encoding='utf-8'
)

def git_push_changes():
    """دالة لرفع التغييرات إلى GitHub"""
    try:
        # تحديد مسار المجلد
        base_dir = Path(__file__).parent
        
        # تنفيذ أوامر Git
        commands = [
            ['gh', 'auth', 'status'],  # التحقق من حالة المصادقة
            ['git', 'add', 'data/certificates.json'],
            ['git', 'commit', '-m', f'تحديث تلقائي للبيانات - {time.strftime("%Y-%m-%d %H:%M:%S")}'],
            ['git', 'pull', '--rebase', 'origin', 'main'],
            ['gh', 'repo', 'sync']  # مزامنة المستودع باستخدام GitHub CLI
        ]
        
        for cmd in commands:
            result = subprocess.run(cmd, cwd=str(base_dir), capture_output=True, text=True)
            if result.returncode != 0:
                if cmd[0] == 'git' and 'nothing to commit' in result.stderr:
                    continue  # تجاهل رسالة "nothing to commit"
                elif cmd[0] == 'gh' and 'auth status' in ' '.join(cmd):
                    logging.error('يرجى تسجيل الدخول إلى GitHub CLI أولاً باستخدام الأمر: gh auth login')
                    return False
                else:
                    logging.error(f'خطأ في تنفيذ الأمر {cmd}: {result.stderr}')
                    return False
            else:
                logging.info(f'تم تنفيذ الأمر {cmd[0]} بنجاح')
        
        return True
    except Exception as e:
        logging.error(f'خطأ في رفع التغييرات إلى GitHub: {str(e)}')
        return False

class ExcelToJsonHandler(FileSystemEventHandler):
    def __init__(self, excel_path, json_path):
        self.excel_path = excel_path
        self.json_path = json_path
        self.last_modified = 0
        self.cooldown = 2  # فترة الانتظار بين التحديثات (بالثواني)

    def on_modified(self, event):
        if not event.is_directory and event.src_path == self.excel_path:
            current_time = time.time()
            if current_time - self.last_modified > self.cooldown:
                self.last_modified = current_time
                self.update_json()

    def update_json(self):
        try:
            # انتظار لحين إغلاق ملف الإكسل
            time.sleep(1)
            
            # قراءة ملف الإكسل مع التعامل مع القيم الفارغة
            df = pd.read_excel(self.excel_path)
            
            # معالجة القيم الفارغة
            df = df.fillna('')  # تحويل NaN إلى نص فارغ
            
            # تحويل البيانات إلى قائمة من القواميس مع الحفاظ على التنسيق
            data = df.to_dict('records')
            
            # التأكد من وجود جميع الأعمدة المطلوبة
            required_columns = [
                'Column1.name', 'Column1.department', 'Column1.employee_name',
                'Column1.employee_courses_degree.certificate_name',
                'Column1.employee_courses_degree.certificate_date',
                'Column1.user_id', 'Column1.gender', 'Column1.date_of_joining',
                'Column1.designation', 'Column1.branch',
                'Column1.employee_courses_degree.attach_the_certificate',
                'urlnext', 'certificate url'
            ]
            
            # إضافة الأعمدة المفقودة إذا لم تكن موجودة
            for record in data:
                for col in required_columns:
                    if col not in record:
                        record[col] = ''
            
            # حفظ البيانات في ملف JSON
            with open(self.json_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            logging.info('تم تحديث ملف JSON بنجاح')
            
            # رفع التغييرات إلى GitHub
            if git_push_changes():
                logging.info('تم رفع التغييرات إلى GitHub بنجاح')
            else:
                logging.error('فشل في رفع التغييرات إلى GitHub')
                
        except Exception as e:
            logging.error(f'حدث خطأ أثناء تحديث ملف JSON: {str(e)}')

class AutoSyncService(win32serviceutil.ServiceFramework):
    _svc_name_ = "CertificatesAutoSync"
    _svc_display_name_ = "Certificates Auto Sync Service"
    _svc_description_ = "خدمة المزامنة التلقائية لشهادات المتدربين"

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.stop_event = win32event.CreateEvent(None, 0, 0, None)
        self.observer = None

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.stop_event)
        if self.observer:
            self.observer.stop()

    def SvcDoRun(self):
        try:
            servicemanager.LogMsg(
                servicemanager.EVENTLOG_INFORMATION_TYPE,
                servicemanager.PID_INFO,
                ('Service started.')
            )
            
            # تحديد مسارات الملفات
            base_dir = Path(__file__).parent
            excel_path = str(base_dir / 'data' / 'certificates.xlsx')
            json_path = str(base_dir / 'data' / 'certificates.json')
            
            # إعداد المراقب
            event_handler = ExcelToJsonHandler(excel_path, json_path)
            self.observer = Observer()
            self.observer.schedule(event_handler, str(Path(excel_path).parent), recursive=False)
            self.observer.start()
            
            # انتظار إشارة التوقف
            win32event.WaitForSingleObject(self.stop_event, win32event.INFINITE)
            
        except Exception as e:
            logging.error(f'خطأ في تشغيل الخدمة: {str(e)}')
            servicemanager.LogErrorMsg(str(e))

def run_as_script():
    """تشغيل البرنامج كسكريبت عادي"""
    try:
        print("بدء مراقبة ملف Excel...")
        logging.info("بدء تشغيل السكريبت في الوضع المباشر")
        
        # تحديد مسارات الملفات
        base_dir = Path(__file__).parent
        excel_path = str(base_dir / 'data' / 'certificates.xlsx')
        json_path = str(base_dir / 'data' / 'certificates.json')
        
        # إعداد المراقب
        event_handler = ExcelToJsonHandler(excel_path, json_path)
        observer = Observer()
        observer.schedule(event_handler, str(Path(excel_path).parent), recursive=False)
        observer.start()
        
        # تحديث الملف مباشرة عند البدء
        event_handler.update_json()
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
            print("\nتم إيقاف المراقبة.")
        
        observer.join()
        
    except Exception as e:
        logging.error(f'خطأ في تشغيل السكريبت: {str(e)}')
        print(f'حدث خطأ: {str(e)}')

if __name__ == '__main__':
    if len(sys.argv) > 1:
        win32serviceutil.HandleCommandLine(AutoSyncService)
    else:
        # تشغيل كسكريبت عادي
        run_as_script()
