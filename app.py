import streamlit as st
from modules.parser import process_bank_statement

st.set_page_config(page_title="Tally Expert", layout="wide")
st.title("🏦 Tally Expert - PNB Statement Parser")

uploaded_file = st.file_uploader("PNB PDF Upload karein", type="pdf")
password = st.text_input("Password (Agar ho toh)", type="password")

if st.button("Process Data"):
    if uploaded_file is not None:
        with st.spinner('Data process ho raha hai...'):
            pwd = password if password != "" else None
            df = process_bank_statement(uploaded_file, pwd, "PNB")
            
            if df is not None:
                # Summary metrics
                col1, col2, col3 = st.columns(3)
                col1.metric("Total Debit", f"₹{df['Debit'].sum():,.2f}")
                col2.metric("Total Credit", f"₹{df['Credit'].sum():,.2f}")
                col3.metric("Total Trans.", len(df))
                
                st.dataframe(df, use_container_width=True)
                
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button("Download CSV for Tally", csv, "Tally_Import.csv", "text/csv")
            else:
                st.error("Error: Data extract nahi hua.")
