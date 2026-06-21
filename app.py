import streamlit as st
from modules.parser import process_bank_statement

st.set_page_config(page_title="Tally Expert", layout="wide")
st.title("🏦 Tally Expert - Bank Statement Parser")

# Sidebar for settings
st.sidebar.header("Settings")
bank = st.sidebar.selectbox("Bank Select karein", ["PNB", "AXIS", "HDFC", "YES"])

# Main Input
uploaded_file = st.file_uploader("PDF Statement Upload karein", type="pdf")
password = st.text_input("PDF Password (Agar ho)", type="password")

if st.button("Process Data"):
    if uploaded_file is not None:
        with st.spinner('Data extract ho raha hai...'):
            df = process_bank_statement(uploaded_file, password, bank)
            
            if df is not None:
                st.success("Extraction Successful!")
                st.dataframe(df, use_container_width=True)
                
                # CSV Download Button
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button("Download CSV for Tally", csv, "statement.csv", "text/csv")
            else:
                st.error("Data extract nahi ho paaya. Password check karein ya file corrupt ho sakti hai.")
    else:
        st.warning("Please file upload karein.")
