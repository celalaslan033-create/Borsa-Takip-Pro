import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="Borsa Takip Pro", layout="wide")
st.title("📈 Borsa Takip Pro - ADIM 1")

BIST = ["AKBNK.IS","ASELS.IS","BIMAS.IS","EREGL.IS","GARAN.IS","THYAO.IS","TUPRS.IS","BRSAN.IS","SASA.IS","SISE.IS"]
GLOBAL = {"BRENT":"BZ=F","ALTIN":"GC=F","GUMUS":"SI=F","NASDAQ":"^IXIC","S&P500":"^GSPC"}

def rsi(s, p=14):
    d=s.diff()
    g=d.where(d>0,0).rolling(p).mean()
    l=-d.where(d<0,0).rolling(p).mean()
    rs=g/l
    return 100-(100/(1+rs))

def macd(s):
    return s.ewm(12).mean()-s.ewm(26).mean()

mod=st.radio("Piyasa",["GLOBAL","BIST","HEPSI"],1,horizontal=True)
liste = list(GLOBAL.keys()) if mod=="GLOBAL" else BIST if mod=="BIST" else BIST+list(GLOBAL.keys())
mp={**{k:k for k in BIST},**GLOBAL}

sec=st.multiselect("Varlik Sec",liste,default=list(GLOBAL.keys()))

@st.cache_data(ttl=90)
def veri(t):
    d=yf.download(t,period="3mo",progress=False,auto_adjust=True)
    if hasattr(d.columns,'get_level_values'): d.columns=d.columns.get_level_values(0)
    return d

if st.button("🚀 ANALIZ ET",type="primary",use_container_width=True):
    rows=[]
    for isim in sec:
        t=mp[isim]
        d=veri(t)
        if d is None or len(d)<50: continue
        close=d['Close']
        fiyat=float(close.iloc[-1])
        deg=(fiyat-float(close.iloc[-2]))/float(close.iloc[-2])*100
        r=float(rsi(close).iloc[-1])
        m=float(macd(close).iloc[-1])
        sma20=float(close.rolling(20).mean().iloc[-1])
        sma50=float(close.rolling(50).mean().iloc[-1])
        sig="SUPER AL" if fiyat>sma20>sma50 and r>55 and m>0 else "AL" if fiyat>sma20 and r>50 else "SAT" if fiyat<sma20 else "BEKLE"
        rows.append({"Varlik":isim,"Fiyat":round(fiyat,2),"Degisim %":round(deg,2),"RSI":round(r,1),"MACD":round(m,3),"Sinyal":sig,"close":close})
    import pandas as pd
    df=pd.DataFrame(rows)
    st.dataframe(df.drop(columns=["close"]),use_container_width=True,hide_index=True)
    if rows:
        sec2=st.selectbox("Grafik",[r["Varlik"] for r in rows])
        d2=next(r for r in rows if r["Varlik"]==sec2)
        st.metric("RSI",d2["RSI"])
        st.line_chart(d2["close"].tail(60))
