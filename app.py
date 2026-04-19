import time
from datetime import datetime

import pandas as pd
import requests
import streamlit as st

st.set_page_config(page_title="BSJP Screener", layout="wide")

API_URL = "https://api-anda.com/bsjp"  # ganti ke endpoint API Anda
API_HEADERS = {
    "Content-Type": "application/json",
    # "Authorization": "Bearer TOKEN_ANDA",
    # "x-api-key": "API_KEY_ANDA",
}
AUTO_REFRESH_SECONDS = 60
DEFAULT_PRICE_CAP = 1000
DEFAULT_ROW_LIMIT = 50


@st.cache_data(ttl=AUTO_REFRESH_SECONDS, show_spinner=False)
def fetch_market_data() -> pd.DataFrame:
    res = requests.get(API_URL, headers=API_HEADERS, timeout=20)
    res.raise_for_status()

    json_data = res.json()
    source_rows = (
        json_data
        if isinstance(json_data, list)
        else json_data.get("data")
        or json_data.get("results")
        or json_data.get("items")
        or []
    )

    records = []
    for item in source_rows:
        now = float(item.get("now") or item.get("price") or item.get("harga") or item.get("last") or item.get("close") or 0)
        entry = float(item.get("entry") or item.get("buy_price") or item.get("entryPrice") or now)
        tp = float(item.get("tp") or item.get("take_profit") or item.get("target") or round(now * 1.04))
        sl = float(item.get("sl") or item.get("stop_loss") or item.get("cutloss") or round(now * 0.96))
        gain1 = float(item.get("gain1") or item.get("gain") or item.get("change_pct") or item.get("changePercent") or 0)
        wick = float(item.get("wick") or item.get("upper_wick") or item.get("wick_pct") or 0)
        rvol = float(item.get("rvol") or item.get("relative_volume") or item.get("rvol_pct") or 0)
        profit = float(item.get("profit") or (((now - entry) / entry) * 100 if entry else 0))
        to_tp = float(item.get("toTp") or item.get("to_tp") or item.get("percent_to_tp") or (((tp - now) / now) * 100 if now else 0))
        rsi5m = float(item.get("rsi5m") or item.get("rsi_5m") or item.get("rsi") or 0)

        action = str(item.get("action") or item.get("aksi") or item.get("recommendation") or "WATCH GC").upper()
        signal = str(item.get("signal") or item.get("sinyal") or item.get("status") or "WAIT").upper()
        rsi_sig = str(item.get("rsiSig") or item.get("rsi_signal") or ("UP" if rsi5m >= 50 else "DEAD")).upper()
        phase = str(item.get("phase") or item.get("fase") or item.get("market_phase") or "NETRAL").upper()
        trend = str(item.get("trend") or item.get("direction") or ("BULL" if gain1 >= 0 else "BEAR")).upper()
        ticker = str(item.get("ticker") or item.get("symbol") or item.get("kode") or item.get("emiten") or "").upper()
        value = float(item.get("value") or item.get("val") or item.get("volume_value") or item.get("turnover") or 0)

        if ticker and now:
            records.append(
                {
                    "Emiten": ticker,
                    "Gain 1 (%)": gain1,
                    "Wick (%)": wick,
                    "Aksi": action,
                    "Sinyal": signal,
                    "RVOL (%)": rvol,
                    "Entry": entry,
                    "Now": now,
                    "TP": tp,
                    "SL": sl,
                    "Profit (%)": profit,
                    "% To TP": to_tp,
                    "RSI Sig": rsi_sig,
                    "RSI 5M": rsi5m,
                    "Val": value,
                    "Fase": phase,
                    "Trend": trend,
                }
            )

    return pd.DataFrame(records)


def style_dataframe(df: pd.DataFrame):
    def color_gain(val):
        if isinstance(val, (int, float)):
            return "color: #16c784; font-weight: 700;" if val >= 0 else "color: #ff5b6e; font-weight: 700;"
        return ""

    def color_trend(val):
        if val == "BULL":
            return "background-color: rgba(22,199,132,.18); color: #16c784; font-weight: 700;"
        if val == "BEAR":
            return "background-color: rgba(255,91,110,.18); color: #ff5b6e; font-weight: 700;"
        return ""

    def color_signal(val):
        txt = str(val).upper()
        if txt in {"ON TRACK", "AKUM", "SUPER", "HAKA"}:
            return "background-color: rgba(22,199,132,.12);"
        if txt in {"DIST"}:
            return "background-color: rgba(255,91,110,.12);"
        if txt in {"REBOUND"}:
            return "background-color: rgba(255,143,61,.12);"
        return ""

    return (
        df.style
        .format(
            {
                "Gain 1 (%)": "{:.1f}",
                "Wick (%)": "{:.1f}",
                "RVOL (%)": "{:.0f}",
                "Entry": "{:.0f}",
                "Now": "{:.0f}",
                "TP": "{:.0f}",
                "SL": "{:.0f}",
                "Profit (%)": "{:.1f}",
                "% To TP": "{:.1f}",
                "RSI 5M": "{:.1f}",
                "Val": "{:,.0f}",
            }
        )
        .applymap(color_gain, subset=["Gain 1 (%)", "Profit (%)"])
        .applymap(color_trend, subset=["Trend"])
        .applymap(color_signal, subset=["Sinyal"])
    )


st.title("BSJP Screener - Streamlit")
st.caption("1 tabel, lebih banyak emiten, filter harga maksimal 1000, auto refresh 60 detik, dan search emiten.")

with st.sidebar:
    st.header("Filter")
    search = st.text_input("Search Emiten", placeholder="Contoh: BBRI, TLKM, BRIS")
    price_cap = st.number_input("Batas Harga Maks", min_value=1, value=DEFAULT_PRICE_CAP, step=1)
    row_limit = st.selectbox("Jumlah Baris", [25, 50, 75, 100], index=1)
    sort_by = st.selectbox(
        "Urutkan",
        ["Gain 1 (%)", "RVOL (%)", "Now", "RSI 5M", "Val"],
        index=0,
    )
    st.caption(f"Auto refresh setiap {AUTO_REFRESH_SECONDS} detik")
    if st.button("Refresh Sekarang", use_container_width=True):
        fetch_market_data.clear()
        st.rerun()

try:
    df = fetch_market_data()
except Exception as err:
    st.error("Gagal mengambil data API. Periksa URL endpoint, header auth, CORS/proxy, dan format response API.")
    st.code(str(err))
    st.stop()

if df.empty:
    st.warning("Tidak ada data dari API.")
    st.stop()

filtered = df[df["Now"] <= price_cap].copy()

if search.strip():
    filtered = filtered[filtered["Emiten"].str.contains(search.strip().upper(), na=False)]

filtered = filtered.sort_values(by=sort_by, ascending=False).head(row_limit)

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Jumlah Emiten Tampil", len(filtered))
col2.metric("Harga Maks Aktif", f"{int(price_cap):,}")
col3.metric("Bull Trend", int((filtered["Trend"] == "BULL").sum()))
col4.metric("Bear Trend", int((filtered["Trend"] == "BEAR").sum()))
col5.metric("Last Update", datetime.now().strftime("%H:%M:%S"))

st.dataframe(style_dataframe(filtered), use_container_width=True, height=720)

st.caption(
    "Ganti API_URL dan API_HEADERS sesuai endpoint Anda. Mapping field sudah dibuat fleksibel untuk key umum seperti ticker/symbol/kode, now/price/harga, gain/change_pct, rsi5m/rsi_5m, dan value/turnover."
)

# auto refresh sederhana
placeholder = st.empty()
with placeholder.container():
    st.caption(f"Halaman akan refresh otomatis setiap {AUTO_REFRESH_SECONDS} detik.")

time.sleep(AUTO_REFRESH_SECONDS)
st.rerun()
