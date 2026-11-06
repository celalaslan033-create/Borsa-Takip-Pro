
import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="Borsa Takip Pro", layout="wide")
st.title("📈 Borsa Takip Pro - BIST Sinyal Paneli")

BIST = ["THYAO.IS","AKBNK.IS","GARAN.IS","ISCTR.IS","EREGL.IS","TUPRS.IS","ASELS.IS","KCHOL.IS","BIMAS.IS"]

secili = st.multiselect("Hisseleri Sec", BIST, default=BIST[:5])

if st.button("🚀 TUMUNU ANALIZ ET", type="primary"):
    sonuclar = []
    for hisse in secili:
        try:
            d = yf.download(hisse, period="6mo", progress=False, auto_adjust=True)
            if d.empty: continue
            if isinstance(d.columns, pd.MultiIndex):
                d.columns = d.columns.get_level_values(0)
            
            close = d['Close']
            sma20 = close.rolling(20).mean().iloc[-1]
            sma50 = close.rolling(50).mean().iloc[-1]
            fiyat = float(close.iloc[-1])
            
            delta = close.diff()
            gain = delta.where(delta > 0, 0).rolling(14).mean().iloc[-1]
            loss = -delta.where(delta < 0, 0).rolling(14).mean().iloc[-1]
            rs = gain / loss if loss != 0 else 1
            rsi = 100 - (100 / (1 + rs))
            
            if fiyat > sma20 and rsi < 70: sinyal = "🟢 AL"
            elif rsi > 70: sinyal = "🔴 SAT"
            else: sinyal = "🟡 BEKLE"
            
            sonuclar.append({"Hisse": hisse.replace(".IS",""), "Fiyat": round(fiyat,2), "RSI": round(float(rsi),1), "Sinyal": sinyal})
        except:
            continue
    
    if sonuclar:
        st.dataframe(pd.DataFrame(sonuclar), use_container_width=True, hide_index=True)
        st.success(f"{len(sonuclar)} hisse analiz edildi!")
    else:
        st.warning("Yahoo verisi su an kapali, demo gosteriliyor")
        demo = [
            {"Hisse":"THYAO","Fiyat":287.5,"RSI":62.3,"Sinyal":"🟢 AL"},
            {"Hisse":"AKBNK","Fiyat":58.2,"RSI":71.1,"Sinyal":"🔴 SAT"},
            {"Hisse":"EREGL","Fiyat":42.8,"RSI":55.0,"Sinyal":"🟢 AL"},
            {"Hisse":"TUPRS","Fiyat":145.3,"RSI":48.2,"Sinyal":"🟡 BEKLE"},
            {"Hisse":"ASELS","Fiyat":62.1,"RSI":65.4,"Sinyal":"🟢 AL"},
        ]
        st.dataframe(pd.DataFrame(demo), use_container_width=True, hide_index=True)
