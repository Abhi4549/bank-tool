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
        
        extracted_rows = []
        with pdfplumber.open(decrypted_stream) as pdf_doc:
            for page in pdf_doc.pages:
                # Table extraction focus
                table = page.extract_table(table_settings={"vertical_strategy": "text", "horizontal_strategy": "text"})
                if table:
                    for row in table:
                        # Row mein se None values hatana
                        clean_row = [str(cell).replace('\n', ' ') if cell else "" for cell in row]
                        
                        # Date pattern check (DD/MM/YYYY)
                        if any(re.search(r'\d{2}/\d{2}/\d{4}', str(cell)) for cell in clean_row):
                            extracted_rows.append(clean_row)
        
        # DataFrame banayein
        df = pd.DataFrame(extracted_rows)
        
        # Column selection (Humein sirf 5 columns chahiye)
        # Agar PDF mein 5 se zyada columns hain, toh hum sirf pehle 5 ya specific index lenge
        if df.shape[1] >= 5:
            df = df.iloc[:, :5]
            df.columns = ['Date', 'Narration', 'Debit', 'Credit', 'Balance']
            
            # Numeric cleaning
            for col in ['Debit', 'Credit', 'Balance']:
                df[col] = df[col].astype(str).str.replace(r'[^\d.]', '', regex=True)
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
                
        return df.drop_duplicates()
    except Exception as e:
        return None
