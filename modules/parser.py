import pandas as pd
import pdfplumber
import pikepdf
import io
import re

def process_bank_statement(uploaded_file, password, bank_name):
    try:
        # Buffer mein file read karein
        file_buffer = io.BytesIO(uploaded_file.read())
        
        # Check if password protected
        try:
            with pikepdf.open(file_buffer) as pdf:
                # Agar code yahan bina error ke chal gaya, toh file protected hai
                # Par hum password try karenge
                pdf = pikepdf.open(file_buffer, password=password)
                decrypted_stream = io.BytesIO()
                pdf.save(decrypted_stream)
                decrypted_stream.seek(0)
                file_buffer = decrypted_stream
        except pikepdf.PasswordError:
            # Agar error aaya, toh file protected nahi hai ya password wrong hai
            # Agar file bina password ke khul rahi hai, toh wahi use karein
            file_buffer.seek(0)
        except Exception:
            # File protected nahi hai
            file_buffer.seek(0)
        
        # Data Extraction
        all_data = []
        with pdfplumber.open(file_buffer) as pdf_doc:
            for page in pdf_doc.pages:
                text = page.extract_text()
                if not text: continue
                
                for line in text.split('\n'):
                    # Date match pattern: DD/MM/YYYY
                    if re.search(r'\d{2}/\d{2}/\d{4}', line):
                        parts = line.split()
                        
                        # Numerical Mapping Logic
                        try:
                            date = parts[0]
                            balance = float(parts[-1].replace(',', ''))
                            # Last 2 numbers ko Amount consider karein
                            val1 = float(parts[-3].replace(',', '')) if parts[-3].replace('.','').isdigit() else 0
                            val2 = float(parts[-2].replace(',', '')) if parts[-2].replace('.','').isdigit() else 0
                            
                            # Debit/Credit Logic
                            debit, credit = (val1, 0) if val1 < 0 else (0, val1)
                            narration = " ".join(parts[1:-3])
                            
                            all_data.append([date, narration, debit, credit, balance])
                        except:
                            continue
        
        df = pd.DataFrame(all_data, columns=['Date', 'Narration', 'Debit', 'Credit', 'Balance'])
        return df.drop_duplicates()
        
    except Exception as e:
        return None
