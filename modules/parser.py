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
        
        all_data = []
        with pdfplumber.open(decrypted_stream) as pdf_doc:
            for page in pdf_doc.pages:
                # 'text' based extraction is more stable than 'table'
                text = page.extract_text()
                if not text: continue
                
                for line in text.split('\n'):
                    # Regex for Date (DD/MM/YYYY)
                    if re.search(r'\d{2}/\d{2}/\d{4}', line):
                        # Line ko parts mein todein
                        parts = line.split()
                        
                        # Numerical Mapping Logic:
                        # Hum assume kar rahe hain Date(0), Narration(1:), Amount1, Amount2, Balance(last)
                        if len(parts) >= 4:
                            date = parts[0]
                            balance = float(parts[-1].replace(',', ''))
                            # Amount extraction (last second, last third)
                            val1 = float(parts[-3].replace(',', '')) if parts[-3].replace('.','').isdigit() else 0
                            val2 = float(parts[-2].replace(',', '')) if parts[-2].replace('.','').isdigit() else 0
                            
                            # Normalization Rule:
                            debit, credit = (val1, 0) if val1 < 0 else (0, val1)
                            
                            all_data.append([date, " ".join(parts[1:-3]), debit, credit, balance])
        
        df = pd.DataFrame(all_data, columns=['Date', 'Narration', 'Debit', 'Credit', 'Balance'])
        return df.drop_duplicates()
    except Exception:
        return None
