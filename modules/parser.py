import pandas as pd
import pdfplumber
import pikepdf
import io
import re

def process_bank_statement(uploaded_file, password, bank_name):
    try:
        # Buffer mein file read
        file_buffer = io.BytesIO(uploaded_file.read())
        
        # 1. Decryption (Optional)
        try:
            with pikepdf.open(file_buffer, password=password) as pdf:
                decrypted_stream = io.BytesIO()
                pdf.save(decrypted_stream)
                decrypted_stream.seek(0)
                file_buffer = decrypted_stream
        except:
            file_buffer.seek(0)
            
        all_rows = []
        with pdfplumber.open(file_buffer) as pdf:
            for page in pdf.pages:
                # PNB ki table extract karo
                table = page.extract_table(table_settings={"vertical_strategy": "text", "horizontal_strategy": "text"})
                if table:
                    for row in table:
                        # Row check: Date format "DD/MM/YYYY"
                        row_str = " ".join([str(c) for c in row if c])
                        if re.search(r'\d{2}/\d{2}/\d{4}', row_str):
                            # Clean each cell
                            clean_row = [str(c).replace('\n', ' ') if c else "" for c in row]
                            all_rows.append(clean_row)
        
        # DataFrame mein convert
        df = pd.DataFrame(all_rows)
        
        # Column Selection (PNB structure: Date, Remarks, Ref, Withdraw, Deposit, Balance)
        # Hum sirf 6 columns le rahe hain
        if df.shape[1] >= 6:
            df = df.iloc[:, [0, 1, 3, 4, 5]]
            df.columns = ['Date', 'Narration', 'Debit', 'Credit', 'Balance']
            
            # Numeric conversion
            for col in ['Debit', 'Credit', 'Balance']:
                df[col] = df[col].astype(str).str.replace(r'[^\d.]', '', regex=True)
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
                
        return df.drop_duplicates()
    except Exception:
        return None
