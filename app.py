import streamlit as st
from modules.parser import process_bank_statement

st.set_page_config(page_title="Tally Expert", layout="wide")
st.title("🏦 Tally Expert - Bank to Tally Converter")

uploaded_file = st.file_uploader("PDF Statement Upload karein", type="pdf")
password = st.text_input("PDF Password", type="password")
bank = st.selectbox("Bank Select karein", ["PNB", "AXIS", "HDFC", "YES"])

if st.button("Process & Clean Data"):
    if uploaded_file and password:
        with st.spinner('Data process ho raha hai...'):
            df = process_bank_statement(uploaded_file, password, bank)
            
            if df is not None:
                st.success("Data Cleaned!")
                st.dataframe(df)
                
                # Download button for Tally
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button("Download CSV for Tally", csv, "Tally_Import.csv", "text/csv")
            else:
                st.error("Extraction fail hua. Password galat ho sakta hai.")
    else:
        st.warning("Please file aur password fill karein.")
