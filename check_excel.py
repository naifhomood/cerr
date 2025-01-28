import pandas as pd
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    # قراءة ملف Excel
    df = pd.read_excel('data/certificates.xlsx')
    
    # طباعة أسماء الأعمدة
    print("\nأسماء الأعمدة في الملف:")
    print("------------------------")
    for col in df.columns:
        print(f"- {col}")
    
    # طباعة عدد الصفوف
    print(f"\nعدد السجلات: {len(df)}")
    
    # طباعة نموذج من البيانات
    print("\nنموذج من البيانات:")
    print("------------------")
    print(df.head(1).to_string())
    
except Exception as e:
    logger.error(f"حدث خطأ: {str(e)}")
