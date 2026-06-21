import pandas as pd
import pdfplumber
import pikepdf
import io

def process_bank_statement(uploaded_file, password, bank_name):
    try:
        # File handle
        file_content = uploaded_file.read()
        file_buffer = io.BytesIO(file_content)
        
        # 1. Decryption/Handling
        try:
            with pikepdf.open(file_buffer, password=password) as pdf:
                decrypted_stream = io.BytesIO()
                pdf.save(decrypted_stream)
                decrypted_stream.seek(0)
                file_buffer = decrypted_stream
        except:
            file_buffer.seek(0)
        
        # 2. Pro-Table Extraction
        all_tables = []
        with pdfplumber.open(file_buffer) as pdf_doc:
            for page in pdf_doc.pages:
                # 'horizontal_strategy': "text" se table lines bina grid ke bhi detect ho jati hain
                table = page.extract_table(table_settings={"horizontal_strategy": "text", "vertical_strategy": "text"})
                if table:
                    all_tables.extend(table)
        
        # 3. Data Cleaning (Professional Level)
        df = pd.DataFrame(all_tables)
        
        # Pehli kuch rows junk hoti hain, unhe hatao
        df = df.dropna(thresh=3) # Sirf wahi row lo jisme kam se kam 3 column bhare ho
        
        # Headers set karo (Assuming row 0 is header)
        df.columns = df.iloc[0]
        df = df[1:]
        
        return df
    except Exception as e:
        return None
