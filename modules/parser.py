import pandas as pd
import pdfplumber
import pikepdf
import io

def process_bank_statement(uploaded_file, password, bank_name):
    try:
        # Decrypt logic
        with pikepdf.open(uploaded_file, password=password) as pdf:
            decrypted_stream = io.BytesIO()
            pdf.save(decrypted_stream)
            decrypted_stream.seek(0)
        
        # Extraction logic
        with pdfplumber.open(decrypted_stream) as pdf_doc:
            all_data = []
            for page in pdf_doc.pages:
                table = page.extract_table()
                if table:
                    all_data.extend(table)
        
        df = pd.DataFrame(all_data[1:], columns=all_data[0])
        # Deduplication
        df = df.drop_duplicates(keep='first')
        return df
    except Exception as e:
        return None
