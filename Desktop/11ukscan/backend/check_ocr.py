import sys
import os
sys.path.append('C:\\Users\\Akash Pandey\\Desktop\\11ukscan\\backend')

from app.ocr.tesseract_ocr import TesseractOCR

try:
    ocr = TesseractOCR()
    # Find the most recently created PDF in the uploads folder
    uploads_dir = r"C:\Users\Akash Pandey\Desktop\11ukscan\backend\uploads"
    pdfs = [os.path.join(uploads_dir, f) for f in os.listdir(uploads_dir) if f.endswith(".pdf")]
    pdfs.sort(key=os.path.getctime, reverse=True)
    if not pdfs:
        print("No PDFs found.")
    else:
        latest_pdf = pdfs[0]
        print(f"Testing {latest_pdf}")
        pages = ocr.extract_text(latest_pdf)
        print("--- PAGE 1 ---")
        print(pages[0][:1000])
except Exception as e:
    import traceback
    traceback.print_exc()
