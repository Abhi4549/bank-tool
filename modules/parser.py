import pandas as pd
import pdfplumber
import pikepdf
import io
import re

def process_bank_statement(uploaded_file, password, bank_name):
    try:
        with pikepdf.open(uploaded_file, password=password) as pdf:
            decrypted_stream = io.BytesIO()
            pdf.save(decrypted_stream)
            decrypted_stream.seek(0)
        
        all_transactions = []
        with pdfplumber.open(decrypted_stream) as pdf_doc:
            for page in pdf_doc.pages:
                text = page.extract_text()
                if not text: continue
                
                # Logic: Har bank ki line ka pattern dhoondo (DD/MM/YYYY)
                lines = text.split('\n')
                for line in lines:
                    # Pattern: Date (DD/MM/YYYY) + Narration + Amounts
                    match = re.search(r'(\d{2}/\d{2}/\d{4})\s+(.*?)\s+([-]?[\d,]+\.\d{2})\s+([-]?[\d,]+\.\d{2})?\s*([\d,]+\.\d{2})?', line)
                    
                    if match:
                        all_transactions.append({
                            'Date': match.group(1),
                            'Narration': match.group(2),
                            'Debit': match.group(3) if float(match.group(3).replace(',','')) < 0 else 0,
                            'Credit': match.group(3) if float(match.group(3).replace(',','')) > 0 else 0,
                            'Balance': match.group(5) or 0
                        })
        
        return pd.DataFrame(all_transactions)
    except Exception as e:
        return None
