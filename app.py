import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="Borsa Takip Pro", layout="wide")
st.title("📈 Borsa Takip Pro - BIST Düzeltildi")

BIST = ["AKBNK.IS","ASELS.IS","BIMAS.IS","EREGL.IS","GARAN.IS","THYAO.IS","TUPRS.IS","BRSAN.IS","SASA.IS","SISE.IS"]
GLOBAL = {"BRENT":"BZ=F","ALTIN":"GC=F","GUMUS":"SI=F","NASDAQ":"^IXIC","SP500":"^GSPC"}

def rsi(s, p=14):
    d=s.diff()
    g=d.where(d>0,0).rolling(p).mean()
    l=-d.where(d<0,0).rolling(p).mean()
    rs=g/l
    return 100-(100/(1+rs))

def macd(s):
    return s.ewm(12).mean()-s.ewm(26).mean()

mod=st.radio("Piyasa",["GLOBAL","BIST","HEPSI"],index=0,horizontal=True)

if mod=="GLOBAL":
    liste=list(GLOBAL.keys())
    mp=GLOBAL
elif mod=="BIST":
    liste=BIST
    mp={k:k for k in BIST}
else:
    liste=BIST+list(GLOBAL.keys())
    mp={**{k:k for k in BIST},**GLOBAL}

sec=st.multiselect("Varlik Sec",liste,default=liste[:3],key=f"sel_{mod}")

@st.cache_data(ttl=90)
def veri(t):
    try:
        d=yf.download(t,period="6mo",progress=False,auto_adjust=True)
        if hasattr(d.columns,'get_level_values'):
            try:
                d.columns=d.columns.get_level_values(0)
            except:
                pass
        return d
    except:
        return None

if st.button("🚀 ANALIZ ET",type="primary",use_container_width=True):
    rows=[]
    hatali=[]
    for isim in sec:
        t=mp[isim]
        d=veri(t)
        if d is None or len(d)<30 or 'Close' not in d.columns:
            hatali.append(isim)
            continue
        close=d['Close'].dropna()
        if len(close)<30:
            hatali.append(isim)
            continue
        fiyat=float(close.iloc[-1])
        deg=(fiyat-float(close.iloc[-2]))/float(close.iloc[-2])*100
        r=float(rsi(close).iloc[-1])
        m=float(macd(close).iloc[-1])
        sma20=float(close.rolling(20).mean().iloc[-1])
        sma50=float(close.rolling(50).mean().iloc[-1])
        if fiyat>sma20>sma50 and r>55 and m>0:
            sig="💎 SUPER AL"
        elif fiyat>sma20 and r>50:
            sig="AL"
        elif fiyat<sma20:
            sig="SAT"
        else:
            sig="BEKLE"
        rows.append({"Varlik":isim,"Fiyat":round(fiyat,2),"Degisim %":round(deg,2),"RSI":round(r,1),"MACD":round(m,3),"Sinyal":sig,"close":close})
    df=pd.DataFrame(rows)
    if hatali:
        st.warning(f"Veri alinamayanlar: {', '.join(hatali)}")
    if len(rows)>0:
        st.dataframe(df.drop(columns=["close"]),use_container_width=True,hide_index=True)
        sel=st.selectbox("Grafik icin sec",[r["Varlik"] for r in rows])
        d2=next(r for r in rows if r["Varlik"]==sel)
        st.metric(f"{sel} Sinyal",d2["Sinyal"])
        st.line_chart(d2["close"].tail(90))
    else:
        st.error("Secili varliklarda veri gelmedi")
