import streamlit as st
from modules.parser import process_bank_statement

st.title("Tally Expert - Bank Tool")

uploaded_file = st.file_uploader("Bank PDF Upload karein", type="pdf")
password = st.text_input("Password", type="password")
bank = st.selectbox("Bank Select karein", ["PNB", "AXIS", "HDFC", "YES"])

if st.button("Process Data"):
    if uploaded_file and password:
        df = process_bank_statement(uploaded_file, password, bank)
        if df is not None:
            st.success("Data Processed!")
            st.dataframe(df)
        else:
            st.error("Error: File read nahi ho paayi.")
