import pandas as pd
import pdfplumber
import pikepdf
import io
import re

def process_bank_statement(uploaded_file, password, bank_name):
    try:
        # Decryption
        with pikepdf.open(uploaded_file, password=password) as pdf:
            decrypted_stream = io.BytesIO()
            pdf.save(decrypted_stream)
            decrypted_stream.seek(0)
        
        extracted_data = []
        with pdfplumber.open(decrypted_stream) as pdf_doc:
            for page in pdf_doc.pages:
                text = page.extract_text()
                if text:
                    for line in text.split('\n'):
                        # Sirf wohi lines lo jisme Date (DD/MM/YYYY) ho
                        if re.search(r'\d{2}/\d{2}/\d{4}', line):
                            parts = line.split()
                            extracted_data.append(parts)
        
        # DataFrame mein convert karo
        df = pd.DataFrame(extracted_data)
        
        # Column mapping (Ye logic aapke bank ke format par depend karega)
        if len(df.columns) >= 4:
            df = df.iloc[:, :4]
            df.columns = ['Date', 'Narration', 'Debit', 'Credit']
            
            # Numeric cleaning for Tally
            df['Debit'] = pd.to_numeric(df['Debit'].str.replace(',', ''), errors='coerce').fillna(0)
            df['Credit'] = pd.to_numeric(df['Credit'].str.replace(',', ''), errors='coerce').fillna(0)
            
        return df.drop_duplicates()
    except Exception:
        return None
