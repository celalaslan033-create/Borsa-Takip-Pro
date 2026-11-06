import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="Borsa Takip Pro", layout="wide")
st.title("📈 Borsa Takip Pro - ANLIK")
st.caption("BIST 100 + GLOBAL Anlik Fiyatlar")

BIST100 = ["AEFES.IS","AGHOL.IS","AKBNK.IS","AKCNS.IS","AKSA.IS","AKSEN.IS","ALARK.IS","ALFAS.IS","ANHYT.IS","ASELS.IS","ASTOR.IS","BIMAS.IS","BRSAN.IS","CCOLA.IS","CIMSA.IS","DOAS.IS","DOHOL.IS","EKGYO.IS","ENJSA.IS","ENKAI.IS","EREGL.IS","FROTO.IS","GARAN.IS","GUBRF.IS","HALKB.IS","HEKTS.IS","ISCTR.IS","KCHOL.IS","KRDMD.IS","KOZAL.IS","MGROS.IS","PETKM.IS","PGSUS.IS","SAHOL.IS","SASA.IS","SISE.IS","TAVHL.IS","TCELL.IS","THYAO.IS","TOASO.IS","TTKOM.IS","TUPRS.IS","YKBNK.IS"]

GLOBAL = {
"BRENT Petrol": "BZ=F",
"ALTIN Ons": "GC=F",
"GUMUS Ons": "SI=F",
"NASDAQ": "^IXIC",
"S&P 500": "^GSPC",
"DOW JONES": "^DJI"
}

mod = st.radio("Piyasa", ["🌍 GLOBAL - Brent, Altin, Gumus, Nasdaq, S&P500, Dow", "🇹🇷 BIST 100", "🔥 HEPSI"], horizontal=True)

if "GLOBAL" in mod:
    sec_list = list(GLOBAL.keys())
    ticker_map = GLOBAL
elif "BIST" in mod:
    sec_list = BIST100
    ticker_map = {k:k for k in BIST100}
else:
    sec_list = BIST100 + list(GLOBAL.keys())
    ticker_map = {**{k:k for k in BIST100}, **GLOBAL}

secili = st.multiselect(f"Varlik Sec ({len(sec_list)})", sec_list, default=list(GLOBAL.keys()) if "GLOBAL" in mod else BIST100[:5])

@st.cache_data(ttl=60)
def cek(t):
    try:
        d = yf.download(t, period="1mo", progress=False, auto_adjust=True)
        if isinstance(d.columns, pd.MultiIndex):
            d.columns = d.columns.get_level_values(0)
        return d
    except:
        return None

if st.button("🚀 ANLIK FIYATLARI GETIR", type="primary"):
    rows = []
    for isim in secili:
        t = ticker_map[isim]
        d = cek(t)
        if d is None or d.empty or len(d) < 5:
            continue
        fiyat = float(d['Close'].iloc[-1])
        onceki = float(d['Close'].iloc[-2])
        deg = (fiyat-onceki)/onceki*100
        
        sma20 = d['Close'].rolling(20).mean()
        sma50 = d['Close'].rolling(50).mean()
        s20 = float(sma20.iloc[-1])
        s50 = float(sma50.iloc[-1])
        
        if fiyat > s20 and s20 > s50:
            sig = "🟢 AL"
        elif fiyat < s20:
            sig = "🔴 SAT"
        else:
            sig = "🟡 BEKLE"
        
        rows.append({"Varlik": isim, "Anlik Fiyat": round(fiyat,2), "Degisim %": round(deg,2), "Sinyal": sig})
    
    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True, hide_index=True)
    st.success(f"Anlik fiyatlar - {pd.Timestamp.now().strftime('%H:%M:%S')}")
    st.caption("Dogrulanmis Tickerlar: BZ=F=Brent ~101$, GC=F=Altin ~4100$, SI=F=Gumus ~52$, ^IXIC=Nasdaq 24315, ^GSPC=S&P 7353, ^DJI=Dow 51523")
