from flask import Flask, render_template, request, send_file
from flask_cors import CORS
import os
from pdf2docx import Converter
from PIL import Image
import pytesseract
import pandas as pd
from docx import Document
from pdf2image import convert_from_path
from datetime import datetime, timedelta
from threading import Thread
import shutil
import time

pytesseract.pytesseract.tesseract_cmd = os.getenv('TESSERACT_PATH', '/usr/bin/tesseract')


app = Flask(__name__)
CORS(app)

# Create folders
UPLOAD_FOLDER = 'uploads'
CONVERTED_FOLDER = 'converted'
for folder in [UPLOAD_FOLDER, CONVERTED_FOLDER]:
    if not os.path.exists(folder):
        os.makedirs(folder)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['CONVERTED_FOLDER'] = CONVERTED_FOLDER

ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def cleanup_old_files():
    """Remove files older than 10 minutes"""
    try:
        current_time = datetime.now()
        for folder in [UPLOAD_FOLDER, CONVERTED_FOLDER]:
            if os.path.exists(folder):
                for filename in os.listdir(folder):
                    filepath = os.path.join(folder, filename)
                    file_time = datetime.fromtimestamp(os.path.getmtime(filepath))
                    if current_time - file_time > timedelta(minutes=10):
                        try:
                            if os.path.isfile(filepath):
                                os.remove(filepath)
                            elif os.path.isdir(filepath):
                                shutil.rmtree(filepath)
                        except Exception as e:
                            print(f"Error removing {filepath}: {str(e)}")
    except Exception as e:
        print(f"Error in cleanup: {str(e)}")

def periodic_cleanup():
    while True:
        cleanup_old_files()
        time.sleep(300)

def convert_pdf_to_word(pdf_path, output_path):
    try:
        # Convert PDF to images
        images = convert_from_path(pdf_path)
        
        # Create Word document
        doc = Document()
        
        # Process each page
        for image in images:
            # Extract text using OCR
            text = pytesseract.image_to_string(image)
            
            # Add text to document
            if text.strip():  # Only add non-empty text
                doc.add_paragraph(text)
            
            # Add page break between pages
            if image != images[-1]:  # Don't add page break after last page
                doc.add_page_break()
        
        # Save the document
        doc.save(output_path)
    except Exception as e:
        raise Exception(f"PDF to Word conversion failed: {str(e)}")

def convert_pdf_to_excel(pdf_path, output_path):
    try:
        # Convert PDF to images
        images = convert_from_path(pdf_path)
        
        # Extract text from all pages
        all_text = []
        for image in images:
            text = pytesseract.image_to_string(image)
            all_text.append(text)
        
        # Combine text and convert to Excel
        combined_text = '\n'.join(all_text)
        df = pd.DataFrame([line.split() for line in combined_text.split('\n') if line.strip()])
        df.to_excel(output_path, index=False)
    except Exception as e:
        raise Exception(f"PDF to Excel conversion failed: {str(e)}")

def convert_image_to_excel(image_path, output_path):
    # Extract text from image using OCR
    image = Image.open(image_path)
    text = pytesseract.image_to_string(image)
    # Convert to Excel
    df = pd.DataFrame([line.split() for line in text.split('\n')])
    df.to_excel(output_path, index=False)

def convert_image_to_word(image_path, output_path):
    # Extract text from image using OCR
    image = Image.open(image_path)
    text = pytesseract.image_to_string(image)
    # Create Word document
    doc = Document()
    doc.add_paragraph(text)
    doc.save(output_path)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    cleanup_old_files()
    # Define max file size (20MB)
    MAX_FILE_SIZE = 20 * 1024 * 1024  # 20MB in bytes
    
    if 'file' not in request.files:
        return 'Please select a file', 400
    
    file = request.files['file']
    output_format = request.form.get('output_format', 'docx')
    
    if file.filename == '':
        return 'No file selected', 400

    # Check file size
    file.seek(0, 2)  # Seek to end of file
    file_size = file.tell()  # Get current position (file size)
    file.seek(0)  # Reset file pointer to beginning
    
    if file_size > MAX_FILE_SIZE:
        return 'File size exceeds 20MB limit', 400

    if file and allowed_file(file.filename):
        # Save original file
        input_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(input_path)
        
        # Generate output filename
        filename_without_ext = os.path.splitext(file.filename)[0]
        output_path = os.path.join(app.config['CONVERTED_FOLDER'], f"{filename_without_ext}.{output_format}")
        
        # Convert based on input type and desired output
        try:
            file_ext = file.filename.rsplit('.', 1)[1].lower()
            
            if file_ext == 'pdf':
                if output_format == 'docx':
                    convert_pdf_to_word(input_path, output_path)
                elif output_format in ['xlsx', 'csv']:
                    convert_pdf_to_excel(input_path, output_path)
            elif file_ext in ['png', 'jpg', 'jpeg', 'gif']:
                if output_format == 'docx':
                    convert_image_to_word(input_path, output_path)
                elif output_format in ['xlsx', 'csv']:
                    convert_image_to_excel(input_path, output_path)
            
            return send_file(output_path, as_attachment=True)
            
        except Exception as e:
            return f'Conversion error: {str(e)}', 500
            
    return 'Unsupported file type', 400

if __name__ == '__main__':
    # Add these lines before app.run
    cleanup_thread = Thread(target=periodic_cleanup, daemon=True)
    cleanup_thread.start()
    
    # Your existing app.run line
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)