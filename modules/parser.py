import pandas as pd
import pdfplumber
import pikepdf
import io
import re

def process_bank_statement(uploaded_file, password, bank_name):
    try:
        # File ko memory mein load karein
        file_content = uploaded_file.read()
        file_buffer = io.BytesIO(file_content)
        
        # 1. TRY: Password-Protected check
        try:
            with pikepdf.open(file_buffer, password=password) as pdf:
                decrypted_stream = io.BytesIO()
                pdf.save(decrypted_stream)
                decrypted_stream.seek(0)
                file_buffer = decrypted_stream
        except:
            # Agar decrypt nahi hua, toh maano bina password ki file hai
            file_buffer.seek(0)
            
        # 2. PRO-LEVEL TABLE EXTRACTION
        all_data = []
        with pdfplumber.open(file_buffer) as pdf_doc:
            for page in pdf_doc.pages:
                # Table settings for max accuracy
                table = page.extract_table(table_settings={
                    "vertical_strategy": "text", 
                    "horizontal_strategy": "text"
                })
                if table:
                    all_data.extend(table)
        
        # 3. CLEANING & FORMATTING
        df = pd.DataFrame(all_data)
        
        # Row cleaning: Jo rows khali hain ya header hain unhe hatao
        # (Hum assume kar rahe hain Date format se rows start hoti hain)
        df = df.dropna(how='all') 
        
        # Column Names (Abhishek, agar column names galat aa rahe hain, toh yahan index set kar sakte ho)
        # Hum 0, 1, 2, 3, 4 index ko standard headers maan rahe hain
        if df.shape[1] >= 5:
            df = df.iloc[:, :5]
            df.columns = ['Date', 'Narration', 'Debit', 'Credit', 'Balance']
            
        return df
        
    except Exception as e:
        return None
