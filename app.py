import streamlit as st
from modules.parser import process_bank_statement

st.set_page_config(layout="wide")
st.title("🏦 Tally Expert - PNB Statement Processor")

uploaded_file = st.file_uploader("PNB PDF Upload karein", type="pdf")
if st.button("Process"):
    if uploaded_file:
        df = process_bank_statement(uploaded_file, None, "PNB")
        if df is not None:
            st.dataframe(df)
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("Download CSV", csv, "Tally.csv", "text/csv")
        else:
            st.error("Data extract nahi ho paya!")
