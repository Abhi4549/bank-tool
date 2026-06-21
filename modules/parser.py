import pandas as pd
import pdfplumber
import pikepdf
import io
import re

def process_bank_statement(uploaded_file, password, bank_name):
    try:
        file_content = uploaded_file.read()
        file_buffer = io.BytesIO(file_content)
        
        # 1. Decryption
        try:
            with pikepdf.open(file_buffer, password=password) as pdf:
                decrypted_stream = io.BytesIO()
                pdf.save(decrypted_stream)
                decrypted_stream.seek(0)
                file_buffer = decrypted_stream
        except:
            file_buffer.seek(0)
            
        # 2. Strict Table Extraction
        all_rows = []
        with pdfplumber.open(file_buffer) as pdf_doc:
            for page in pdf_doc.pages:
                # Sirf table area dhoondhna
                table = page.extract_table(table_settings={"vertical_strategy": "text", "horizontal_strategy": "text"})
                if table:
                    for row in table:
                        # Row filter: Date format (DD/MM/YYYY) dhoondo
                        row_str = " ".join([str(cell) for cell in row if cell])
                        if re.search(r'\d{2}/\d{2}/\d{4}', row_str):
                            all_rows.append(row)
        
        # 3. DataFrame construction
        df = pd.DataFrame(all_rows)
        
        # 4. Column Alignment Fix: Agar 5 column se zyada hain toh unhe trim karo
        if df.shape[1] >= 5:
            df = df.iloc[:, :5]
            df.columns = ['Date', 'Narration', 'Debit', 'Credit', 'Balance']
            
            # Numeric conversion (Clean data for Tally)
            for col in ['Debit', 'Credit', 'Balance']:
                df[col] = df[col].astype(str).str.replace(r'[^\d.]', '', regex=True)
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
                
        return df.drop_duplicates()
        
    except Exception:
        return None
