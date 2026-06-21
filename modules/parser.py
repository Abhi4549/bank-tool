import pandas as pd
import pdfplumber
import io
import re

def process_bank_statement(uploaded_file, password, bank_name):
    # PNB file ke liye optimized logic
    try:
        all_data = []
        with pdfplumber.open(uploaded_file) as pdf:
            for page in pdf.pages:
                # Text extract karo
                text = page.extract_text()
                if not text: continue
                
                # Har line ko check karo
                for line in text.split('\n'):
                    # PNB pattern: Date + Remarks + RefNo + Withdraw + Deposit + Balance
                    # Regex se date dhoondo
                    if re.match(r'\d{2}/\d{2}/\d{4}', line):
                        # Line ko split karo aur cleaning karo
                        parts = line.split()
                        
                        # Logic: PNB ka structure fix hai
                        # 0:Date, 1:Remarks (mixed), -3:Withdraw, -2:Deposit, -1:Balance
                        date = parts[0]
                        withdraw = parts[-3].replace('₹', '').replace(',', '')
                        deposit = parts[-2].replace('₹', '').replace(',', '')
                        balance = parts[-1].replace('₹', '').replace(',', '')
                        narration = " ".join(parts[1:-3])
                        
                        all_data.append([date, narration, withdraw, deposit, balance])
        
        df = pd.DataFrame(all_data, columns=['Date', 'Narration', 'Debit', 'Credit', 'Balance'])
        return df
        
    except Exception as e:
        return None
