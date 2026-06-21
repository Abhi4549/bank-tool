import pandas as pd
import pdfplumber
import io

def process_bank_statement(uploaded_file, password, bank_name):
    try:
        all_data = []
        with pdfplumber.open(uploaded_file) as pdf:
            for page in pdf.pages:
                # Table extract karo (Grid lines ke bina bhi ye 'text' strategy se kaam karega)
                table = page.extract_table(table_settings={
                    "vertical_strategy": "text", 
                    "horizontal_strategy": "text"
                })
                if table:
                    for row in table:
                        # Row mein null values hatao
                        clean_row = [str(cell).replace('\n', ' ') if cell else "" for cell in row]
                        
                        # Date match (DD/MM/YYYY)
                        row_str = " ".join(clean_row)
                        if any(c for c in row_str if '/' in c and len(c) > 5): # Basic date check
                            all_data.append(clean_row)
        
        # DataFrame banayein
        df = pd.DataFrame(all_data)
        
        # PNB Columns (Humne check kiya hai ki Date, Remarks, Ref, Withdraw, Deposit, Balance)
        # Humein sirf Date, Remarks, Withdraw, Deposit, Balance chahiye
        if df.shape[1] >= 6:
            df = df[[0, 1, 3, 4, 5]]
            df.columns = ['Date', 'Narration', 'Debit', 'Credit', 'Balance']
            
            # Numeric cleaning
            for col in ['Debit', 'Credit', 'Balance']:
                df[col] = df[col].astype(str).str.replace(r'[^\d.]', '', regex=True)
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
                
        return df
    except Exception:
        return None
