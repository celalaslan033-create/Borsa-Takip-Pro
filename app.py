
import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="Borsa Takip Pro", layout="wide")
st.title("📈 Borsa Takip Pro - BIST Sinyal Paneli")

BIST = ["THYAO.IS","AKBNK.IS","GARAN.IS","ISCTR.IS","YKBNK.IS","EREGL.IS","TUPRS.IS","ASELS.IS","KCHOL.IS","SAHOL.IS","BIMAS.IS","FROTO.IS","PETKM.IS","SISE.IS","SASA.IS","PGSUS.IS","EKGYO.IS","KOZAL.IS","TCELL.IS","TOASO.IS"]

secili = st.multiselect("Hisseleri Sec", BIST, default=["THYAO.IS","AKBNK.IS","EREGL.IS","TUPRS.IS","ASELS.IS"])

if st.button("🚀 TUMUNU ANALIZ ET", type="primary"):
    sonuclar = []
    prog = st.progress(0)
    for i, hisse in enumerate(secili):
        try:
            d = yf.download(hisse, period="3mo", interval="1d", progress=False)
            if d.empty: continue
            d['SMA20'] = d['Close'].rolling(20).mean()
            d['SMA50'] = d['Close'].rolling(50).mean()
            delta = d['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
            rs = gain / loss
            d['RSI'] = 100 - (100 / (1 + rs))
            fiyat = float(d['Close'].iloc[-1])
            rsi = float(d['RSI'].iloc[-1])
            sma20 = float(d['SMA20'].iloc[-1])
            sma50 = float(d['SMA50'].iloc[-1])
            if fiyat > sma20 and fiyat > sma50 and rsi < 70 and rsi > 50:
                sinyal = "🟢 GUCLU AL"
            elif fiyat > sma20 and rsi < 70:
                sinyal = "🟢 AL"
            elif rsi > 70:
                sinyal = "🔴 SAT"
            elif fiyat < sma20 and fiyat < sma50:
                sinyal = "🔴 GUCLU SAT"
            else:
                sinyal = "🟡 BEKLE"
            sonuclar.append({"Hisse":hisse.replace(".IS",""), "Fiyat":round(fiyat,2), "RSI":round(rsi,1), "Sinyal":sinyal})
        except: continue
        prog.progress((i+1)/len(secili))
    prog.empty()
    df = pd.DataFrame(sonuclar)
    st.dataframe(df, use_container_width=True, hide_index=True)
    st.success(f"{len(df)} hisse analiz edildi!")
