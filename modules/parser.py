import pandas as pd
import pdfplumber
import pikepdf
import io
import re

def process_bank_statement(uploaded_file, password, bank_name):
    # Stream ko memory mein copy karein
    file_content = uploaded_file.read()
    file_buffer = io.BytesIO(file_content)
    
    # 1. TRY: Direct open (Bina password wali files ke liye)
    try:
        with pdfplumber.open(file_buffer) as pdf_doc:
            return extract_data_from_pdf(pdf_doc)
    except:
        # 2. CATCH: Agar error aaya, toh ho sakta hai password protected ho
        try:
            file_buffer.seek(0)
            with pikepdf.open(file_buffer, password=password) as pdf:
                decrypted_stream = io.BytesIO()
                pdf.save(decrypted_stream)
                decrypted_stream.seek(0)
            
            with pdfplumber.open(decrypted_stream) as pdf_doc:
                return extract_data_from_pdf(pdf_doc)
        except:
            return None

def extract_data_from_pdf(pdf_doc):
    all_data = []
    for page in pdf_doc.pages:
        text = page.extract_text()
        if not text: continue
        for line in text.split('\n'):
            if re.search(r'\d{2}/\d{2}/\d{4}', line): # Date check
                parts = line.split()
                # Tally format mapping
                try:
                    all_data.append([parts[0], " ".join(parts[1:-3]), parts[-3], parts[-2], parts[-1]])
                except: continue
    
    df = pd.DataFrame(all_data, columns=['Date', 'Narration', 'Debit', 'Credit', 'Balance'])
    return df
