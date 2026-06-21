import pandas as pd
import pdfplumber
import pikepdf
import io

def process_bank_statement(uploaded_file, password, bank_name):
    try:
        # 1. Decryption
        with pikepdf.open(uploaded_file, password=password) as pdf:
            decrypted_stream = io.BytesIO()
            pdf.save(decrypted_stream)
            decrypted_stream.seek(0)
        
        # 2. Extraction
        all_rows = []
        with pdfplumber.open(decrypted_stream) as pdf_doc:
            for page in pdf_doc.pages:
                text = page.extract_text()
                if text:
                    for line in text.split('\n'):
                        # Line ko space se split karke list mein convert karna
                        columns = line.split()
                        if len(columns) >= 3: # Sirf wo line jisme kam se kam 3 words ho
                            all_rows.append(columns)
        
        # 3. DataFrame Conversion
        # Pehli line ko header manna
        if not all_rows:
            return None
            
        df = pd.DataFrame(all_rows[1:], columns=all_rows[0] if len(all_rows[0]) == len(all_rows[1]) else None)
        
        # 4. Cleaning (Duplicates hatana)
        df = df.drop_duplicates(keep='first')
        
        # 5. Reset index
        df = df.reset_index(drop=True)
        
        return df

    except Exception as e:
        return None
