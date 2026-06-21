import streamlit as st
from modules.parser import process_bank_statement

st.set_page_config(page_title="Tally Expert", layout="wide")
st.title("🏦 Tally Expert - Bank Statement Parser")

uploaded_file = st.file_uploader("PDF Statement Upload karein", type="pdf")
# Password ko optional rakha hai
password = st.text_input("PDF Password (Agar ho, toh daalein)", type="password")
bank = st.selectbox("Bank Select karein", ["PNB", "AXIS", "HDFC", "YES"])

if st.button("Process & Clean Data"):
    if uploaded_file is not None:
        with st.spinner('Data process ho raha hai...'):
            # Password agar khali hai, toh hum 'None' bhejenge
            pwd = password if password != "" else None
            
            df = process_bank_statement(uploaded_file, pwd, bank)
            
            if df is not None:
                st.success("Data Cleaned!")
                st.dataframe(df)
                
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button("Download CSV for Tally", csv, "Tally_Import.csv", "text/csv")
            else:
                st.error("Extraction fail hua. Ho sakta hai file password-protected ho aur password galat ho.")
    else:
        st.warning("Please file upload karein.")
