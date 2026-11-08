import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="Borsa Takip Pro", layout="wide")
st.title("📈 Borsa Takip Pro - BIST 100")

BIST100=["AKBNK.IS","GARAN.IS","ISCTR.IS","YKBNK.IS","THYAO.IS","EREGL.IS","SAHOL.IS","KCHOL.IS","BIMAS.IS","ASELS.IS","TUPRS.IS","SISE.IS","PETKM.IS","FROTO.IS","TOASO.IS","EKGYO.IS","TCELL.IS","AKSA.IS","ARCLK.IS","PGSUS.IS","SASA.IS","HEKTS.IS","GUBRF.IS","KRDMD.IS","KOZAL.IS","KOZAA.IS","ALARK.IS","ENKAI.IS","ODAS.IS","DOHOL.IS","VAKBN.IS","HALKB.IS","TSKB.IS","SKBNK.IS","TTKOM.IS","MGROS.IS","CCOLA.IS","AEFES.IS","MAVI.IS","OTKAR.IS","CIMSA.IS","OYAKC.IS","SOKM.IS","TAVHL.IS","DOAS.IS","ALFAS.IS","ASTOR.IS","CWENE.IS","EUPWR.IS","GESAN.IS","KONTR.IS","SMRTG.IS","SDTTR.IS","REEDR.IS","MIATK.IS","SAYAS.IS","KCAER.IS","GWIND.IS","AKSEN.IS","EGEEN.IS","TTRAK.IS","BRYAT.IS","BRSAN.IS","EREGL.IS","SAHOL.IS","TKFEN.IS","TMSN.IS","KLSER.IS","QUAGR.IS","BIOEN.IS","CANTE.IS","ECILC.IS","ECZYT.IS","ENJSA.IS","ENERY.IS","ULKER.IS","VESBE.IS","VESTL.IS","YYLGD.IS","ZOREN.IS","KONYA.IS","IZENR.IS","KMPUR.IS","ALGYO.IS","BRISA.IS","CLEBI.IS","KZBGY.IS","SELEC.IS","TUKAS.IS","IPEKE.IS","ISMEN.IS","BUCIM.IS","BERA.IS"]

BIST100=list(dict.fromkeys(BIST100))
GLOBAL={"BRENT":"BZ=F","ALTIN":"GC=F","NASDAQ":"^IXIC","BTC":"BTC-USD"}

def rsi(s,p=14):
 d=s.diff(); g=d.where(d>0,0).rolling(p).mean(); l=-d.where(d<0,0).rolling(p).mean()
 return 100-(100/(1+g/l))
def macd(s): return s.ewm(12).mean()-s.ewm(26).mean()

mod=st.radio("Piyasa",["BIST 100","GLOBAL","HEPSI"],0,horizontal=True)
if mod=="GLOBAL": liste=list(GLOBAL.keys()); mp=GLOBAL
elif mod=="BIST 100": liste=BIST100; mp={k:k for k in BIST100}
else: liste=BIST100+list(GLOBAL.keys()); mp={**{k:k for k in BIST100},**GLOBAL}

sec=st.multiselect(f"Hisse Sec ({len(liste)} adet)",liste,default=liste[:5],key=f"sec_{mod}")

@st.cache_data(ttl=90)
def veri(t):
 try:
  d=yf.download(t,period="6mo",progress=False,auto_adjust=True)
  if hasattr(d.columns,'get_level_values'):
   try: d.columns=d.columns.get_level_values(0)
   except: pass
  return d
 except: return None

if st.button("🚀 ANALIZ ET",type="primary",use_container_width=True):
 rows=[]; hatali=[]
 prog=st.progress(0,text=f"{len(sec)} taraniyor...")
 for i,isim in enumerate(sec):
  prog.progress((i+1)/len(sec),text=f"{isim}")
  d=veri(mp[isim])
  if d is None or len(d)<30 or 'Close' not in d.columns: hatali.append(isim); continue
  close=d['Close'].dropna()
  if len(close)<30: hatali.append(isim); continue
  fiyat=float(close.iloc[-1]); deg=(fiyat-float(close.iloc[-2]))/float(close.iloc[-2])*100
  r=float(rsi(close).iloc[-1]); m=float(macd(close).iloc[-1])
  sma20=float(close.rolling(20).mean().iloc[-1]); sma50=float(close.rolling(50).mean().iloc[-1])
  if fiyat>sma20>sma50 and r>55 and m>0: sig="💎 SUPER AL"
  elif fiyat>sma20 and r>50: sig="AL"
  elif fiyat<sma20: sig="SAT"
  else: sig="BEKLE"
  rows.append({"Hisse":isim,"Fiyat":round(fiyat,2),"Degisim %":round(deg,2),"RSI":round(r,1),"Sinyal":sig,"close":close})
 prog.empty()
 df=pd.DataFrame(rows)
 if hatali: st.warning(f"Yahoo atladı: {', '.join(hatali)}")
 if len(rows)>0:
  st.success(f"{len(rows)} hisse analiz edildi!")
  st.dataframe(df.drop(columns=["close"]),use_container_width=True,hide_index=True)
  sel=st.selectbox("Grafik",[r["Hisse"] for r in rows]); d2=next(r for r in rows if r["Hisse"]==sel)
  st.metric(sel,d2["Sinyal"]); st.line_chart(d2["close"].tail(90))
 else: st.error("Veri gelmedi, daha az hisse sec")
