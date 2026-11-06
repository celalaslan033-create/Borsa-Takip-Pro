import streamlit as st
import yfinance as yf

st.title("Borsa Takip Pro")
hisse = st.text_input("Hisse Kodu", "THYAO.IS")
if st.button("Goster"):
    d = yf.download(hisse, period="3mo")
    st.line_chart(d['Close'])
    st.write(d.tail())
