File Converter
Web-based converter for PDF and images to Word/Excel with OCR capabilities.
Features

PDF/Images → Word/Excel conversion
OCR via Tesseract
20MB file limit
Auto cleanup
CORS enabled

Installation

Clone repository
Install dependencies: pip install -r requirements.txt
Install Tesseract OCR
Run: python app.py

Dependencies

Flask==3.0.0
flask-cors==4.0.0
pdf2docx==0.5.6
Pillow==10.2.0
pytesseract==0.3.10
pandas==2.1.4
python-docx==1.0.0
pdf2image==1.16.3

Attributions

pytesseract (Apache 2.0) - OCR engine
pdf2docx (MIT) - PDF conversion
Flask (BSD) - Web framework
Pillow (HPND) - Image processing
pandas (BSD) - Data handling
python-docx (MIT) - Word document creation
pdf2image (MIT) - PDF processing

License
MIT License - see LICENSE file
Disclaimer
OCR accuracy depends on image quality. Software provided as-is without warranty.