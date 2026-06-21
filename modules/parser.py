import pandas as pd
import pdfplumber
import pikepdf
import io
import re

def process_bank_statement(uploaded_file, password, bank_name):
    # PNB specific logic
    try:
        file_buffer = io.BytesIO(uploaded_file.read())
        
        # 1. Decrypt/Open
        try:
            with pikepdf.open(file_buffer, password=password) as pdf:
                decrypted_stream = io.BytesIO()
                pdf.save(decrypted_stream)
                decrypted_stream.seek(0)
                file_buffer = decrypted_stream
        except:
            file_buffer.seek(0)
            
        all_data = []
        with pdfplumber.open(file_buffer) as pdf_doc:
            for page in pdf_doc.pages:
                # PNB table structure
                table = page.extract_table(table_settings={
                    "vertical_strategy": "text", 
                    "horizontal_strategy": "text"
                })
                
                if table:
                    for row in table:
                        # Row filter: Date format check
                        row_str = " ".join([str(cell) for cell in row if cell])
                        if re.search(r'\d{2}/\d{2}/\d{4}', row_str):
                            all_data.append(row)
        
        # DataFrame Cleanup
        df = pd.DataFrame(all_data)
        
        # PNB Columns Mapping (Statement ke hisaab se)
        # 0:Date, 1:Remarks, 2:RefNo, 3:Withdraw, 4:Deposit, 5:Balance
        df = df.iloc[:, [0, 1, 3, 4, 5]]
        df.columns = ['Date', 'Narration', 'Debit', 'Credit', 'Balance']
        
        # Cleaning: Remove symbols like ₹ and commas
        for col in ['Debit', 'Credit', 'Balance']:
            df[col] = df[col].astype(str).str.replace(r'[^\d.]', '', regex=True)
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            
        return df
        
    except Exception as e:
        return None
