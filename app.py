import requests
import textwrap
from datetime import datetime
import numpy as np
import pandas as pd
import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import streamlit.components.v1 as components

st.set_page_config(page_title="High Prob Screener", layout="wide")

# =========================================================
# WATCHLIST MASTER
# =========================================================
SYMBOLS = [
"AALI","ABBA","ABDA","ABMM","ACES","ACST","ADCP","ADES","ADHI","ADMF","ADMG","ADMR","ADRO","AGAR","AGII","AGRO","AGRS","AHAP","AIMS","AISA","AKKU","AKPI","AKRA","AKSI","ALDO","ALKA","ALMI","ALTO","AMAG","AMAR","AMFG","AMIN","AMMN","AMOR","AMRT","ANDI","ANJT","ANTM","APEX","APIC","APII","APLI","APLN","ARCI","ARGO","ARKA","ARMY","ARTA","ARTI","ASBI","ASDM","ASGR","ASII","ASJT","ASMI","ASRI","ASRM","ASSA","ATAP","ATIC","AUTO","AVIA","AXIO",
"BACA","BAJA","BALI","BANK","BAPA","BAPI","BATA","BBCA","BBHI","BBKP","BBLD","BBMD","BBNI","BBRI","BBTN","BBYB","BCAP","BCIC","BCIP","BDMN","BEKS","BEST","BFIN","BHAT","BHIT","BIKA","BIMA","BINA","BIPI","BJBR","BJTM","BKDP","BKSL","BLTA","BLUE","BMAS","BMRI","BMSR","BMTR","BNBA","BNBR","BNGA","BNII","BNLI","BOLA","BOSS","BPFI","BPII","BRAM","BRIS","BRMS","BRNA","BRPT","BSDE","BSSR","BTEL","BTON","BTPN","BTPS","BUKA","BULL","BUMI","BUVA","BVIC",
"CAMP","CANI","CARE","CARS","CBMF","CBUT","CCSI","CEKA","CENT","CFIN","CGAS","CHEM","CINT","CITA","CITY","CLAY","CLEO","CMNP","CMRY","CNKO","CNMA","COAL","CODE","CPIN","CPRO","CSAP","CSIS","CTBN","CTRA","CTTH","CUAN",
"DADA","DART","DAYA","DEAL","DEFI","DEPO","DEWA","DGIK","DILD","DKFT","DLTA","DMAS","DNAR","DOID","DPNS","DSFI","DSNG","DSSA","DUTI","DVLA","EDGE","EKAD","ELSA","EMDE","EMTK","ENAK","ENRG","ENVY","EPAC","ERAA","ESSA","ESTA","ETWA","FAPA","FASW","FILM","FINN","FIRE","FISH","FLMC","FMII","FPNI","FREN","GAMA","GDST","GEMS","GGRM","GIAA","GJTL","GLVA","GMFI","GOLD","GOOD","GPRA","GSMF","GTRA","GTSI","GULA",
"HADI","HAIS","HAPS","HATM","HDFA","HDIT","HEAL","HELI","HERO","HEXA","HITS","HKMU","HKTI","HMSP","HOPE","HRME","HRTA","HUMI","HYAM","IBST","ICBP","ICON","IDEA","IDPR","IFII","IGAR","IIKP","IKAI","IKBI","IKPM","IMAS","IMJS","IMPC","INAF","INAI","INCF","INCI","INCO","INDF","INDR","INDX","INDY","INKP","INOV","INPC","INPP","INTA","INTP","IPCC","IPCM","IPOL","ISAT","ISSP","ITIC","ITMG",
"JARR","JAST","JAYA","JECC","JGLE","JIHD","JKON","JKSW","JMAS","JPFA","JRPT","JSKY","KAEF","KARW","KAYU","KBAG","KBLM","KBLV","KBRI","KDSI","KICI","KINO","KIOS","KKGI","KLBF","KMDS","KMTR","KOBX","KOIN","KONI","KOPI","KPAS","KPIG","KRAS","KREN","LABA","LAPD","LCGP","LEAD","LIFE","LINK","LION","LMAS","LMPI","LMSH","LPCK","LPIN","LPKR","LPLI","LSIP","LTLS","LUCY",
"MAIN","MAPA","MAPB","MARK","MASA","MAYA","MBAP","MBSS","MCAS","MCOL","MDIA","MDKA","MDLN","MEDC","MEGA","MERK","META","MFIN","MFMI","MGNA","MGRO","MICE","MIDI","MIKA","MIRA","MITI","MKNT","MLBI","MLIA","MLPL","MLPT","MMIX","MMLP","MNCN","MNCS","MNTO","MPMX","MPPA","MRAT","MREI","MSIN","MSKY","MTDL","MTFN","MTLA","MTMH","MTPS","MTSM","MYOH","MYOR",
"NANO","NASA","NELY","NFCX","NICK","NICL","NIRO","NISP","NKON","NOBU","NRCA","NTBK","NUSA","OASA","OCAP","OILS","OKAS","OMRE","OPMS","OPTI","ORIN","PACK","PALM","PAMG","PANI","PANS","PBID","PBRX","PCAR","PEGE","PGAS","PGEO","PGLI","PGUN","PICO","PINA","PIPP","PKPK","PLAS","PLIN","PMJS","PNBN","PNBS","PNGO","PNIN","PNLF","POLA","POLI","POLU","POOL","PPGL","PPRE","PRAS","PRDA","PRIM","PSAB","PSDN","PSGO","PSKT","PSSI","PTBA","PTIS","PTPP","PTRO","PTSN","PTSP","PURE","PWON",
"RAAM","RAJA","RALS","RANC","RBMS","RDTX","REAL","RELI","RICY","RIGS","RISE","RMBA","RODA","ROTI","RUIS","SAME","SAMF","SAPX","SATU","SBAT","SBCO","SBER","SBMA","SCBD","SCMA","SDMU","SDPC","SDRA","SGER","SGRO","SIDO","SILO","SIMA","SIMP","SING","SIPD","SKBM","SKLT","SKRN","SMAR","SMBR","SMCB","SMDR","SMGR","SMIL","SMKL","SMKM","SMMA","SMMT","SMRA","SMSM","SNLK","SOCI","SOHO","SONA","SPMA","SPTO","SRAJ","SRTG","SSIA","SSMS","SSTM","STAR","STTP","SULI","SUPR","SURYA","SWAT",
"TALF","TAMA","TAMU","TAPG","TARA","TAXI","TBIG","TBLA","TBMS","TCID","TCPI","TDPM","TEBE","TECH","TELE","TFAS","TFCO","TGKA","TGRA","TIFA","TINS","TKIM","TLKM","TMAS","TOBA","TOOL","TOPS","TOTL","TOTO","TOWR","TPIA","TPMA","TRAM","TRIM","TRIN","TRIO","TRIS","TRJA","TRUK","TSPC",
"UANG","UFOE","ULTJ","UNIC","UNIQ","UNIT","UNSP","UNTR","UNVR","VAST","VICO","VINS","VIVA","VKTR","WAPO","WEGE","WICO","WIDI","WIIM","WIKA","WINE","WINR","WINS","WIRG","WIRY","WOMF","WOOD","YELO","YPAS","YULE","ZBRA","ZINC"
]

MAX_PRICE = 1000
TOP_N = 50
WATCHLISTS = {
    "IDX Top 100": SYMBOLS[:100],
    "IDX Top 800": SYMBOLS[:800],
    "All Master": SYMBOLS,
    "Custom": []
}

# =========================================================
# GLOBAL STYLE
# =========================================================
st.markdown("""
<style>
html, body, [class*="css"] {
    background-color: #081018;
    color: white;
}
.block-container {
    max-width: 99%;
    padding-top: 0.8rem;
    padding-bottom: 1rem;
}
[data-testid="stAppViewContainer"] {
    background: linear-gradient(180deg, #071019 0%, #0a1320 100%);
}
[data-testid="stSidebar"] {
    background-color: #09111d;
}
h1, h2, h3, h4, h5, h6, p, span, div, label {
    color: #e8f0ff !important;
}
.small-note {
    font-size: 12px;
    color: #9db1cc !important;
}
</style>
""", unsafe_allow_html=True)

# =========================================================
# AUTO REFRESH
# =========================================================
def auto_refresh_fragment(seconds: int):
    st.markdown(
        f"""
        <script>
        setTimeout(function() {{
            window.parent.location.reload();
        }}, {seconds * 1000});
        </script>
        """,
        unsafe_allow_html=True
    )

# =========================================================
# HELPERS
# =========================================================
def normalize_jk_symbol(symbol: str) -> str:
    s = symbol.strip().upper()
    if not s:
        return ""
    if ":" in s:
        return s
    if not s.endswith(".JK"):
        s = f"{s}.JK"
    return s


def latest(series: pd.Series) -> float:
    try:
        return float(series.iloc[-1])
    except Exception:
        return np.nan


def fmt_price(v):
    if pd.isna(v):
        return "-"
    if v >= 100:
        return f"{v:,.0f}"
    return f"{v:,.2f}"


def fmt_pct(v):
    if pd.isna(v):
        return "-"
    return f"{v:.1f}%"


def rsi_cell_text(v):
    if pd.isna(v):
        return "-"
    return f"{v:.1f}"


def human_value(v):
    if pd.isna(v):
        return "-"
    if v >= 1_000_000_000_000:
        return f"{v / 1_000_000_000_000:.1f}T"
    if v >= 1_000_000_000:
        return f"{v / 1_000_000_000:.1f}B"
    if v >= 1_000_000:
        return f"{v / 1_000_000:.1f}M"
    return f"{v:,.0f}"

# =========================================================
# TELEGRAM
# =========================================================
def send_telegram_message(bot_token: str, chat_id: str, message: str):
    if not bot_token or not chat_id:
        return False, "Bot token / chat_id kosong"

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }

    try:
        r = requests.post(url, json=payload, timeout=15)
        if r.status_code == 200:
            return True, "Terkirim"
        return False, f"HTTP {r.status_code}: {r.text}"
    except Exception as e:
        return False, str(e)


def build_telegram_watchlist_message(df: pd.DataFrame, top_n: int = 5):
    if df.empty:
        return "📭 <b>Tidak ada saham yang lolos filter</b>"

    scan_time = st.session_state.get("last_run", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    picked = df.head(top_n)
    lines = ["🚨 <b>HIGH PROB SCREENER</b>", f"🕒 <b>{scan_time}</b>", ""]

    for i, (_, row) in enumerate(picked.iterrows(), start=1):
        signal = str(row["sinyal"]).upper()
        trend = str(row["trend"]).upper()
        fase = str(row["fase"]).upper()

        if signal == "SUPER":
            signal_emoji = "🚀"
        elif signal in ["AKUM", "ON TRACK", "HAKA", "GC NOW"]:
            signal_emoji = "✅"
        elif signal == "REBOUND":
            signal_emoji = "🔄"
        elif signal in ["DIST", "WASPADA OB"]:
            signal_emoji = "⚠️"
        else:
            signal_emoji = "⏳"

        trend_emoji = "📈" if trend == "BULL" else "📉" if trend == "BEAR" else "➡️"
        fase_emoji = "🐂" if fase in ["AKUM", "BIG AKUM"] else "🐻" if fase in ["DIST", "BIG DIST"] else "⚪"
        score_emoji = "🏆" if row["score_accum"] >= 70 else "🔥" if row["score_accum"] >= 55 else "⭐" if row["score_accum"] >= 40 else "▫️"
        rvol_emoji = "💥" if row["rvol"] >= 250 else "⚡" if row["rvol"] >= 150 else "🔋" if row["rvol"] >= 100 else "🔹"

        lines.append(f"<b>{i}. {signal_emoji} {row['symbol']}</b>")
        lines.append(
            f"💰 <b>{fmt_price(row['now'])}</b> | "
            f"🎯 <b>{fmt_price(row['entry'])}</b> | "
            f"🏁 <b>{fmt_price(row['tp'])}</b> | "
            f"🛑 <b>{fmt_price(row['sl'])}</b>"
        )
        lines.append(
            f"{score_emoji} Akum <b>{int(row['score_accum'])}</b> | "
            f"🧠 Total <b>{int(row['score_total'])}</b> | "
            f"{rvol_emoji} RVOL <b>{fmt_pct(row['rvol'])}</b>"
        )
        lines.append(
            f"⚡ Scalp <b>{int(row['score_scalping'])}</b> | "
            f"🎯 BSJP <b>{int(row['score_bsjp'])}</b> | "
            f"📈 Swing <b>{int(row['score_swing'])}</b> | "
            f"🏦 Bandar <b>{int(row['score_bandar'])}</b>"
        )
        lines.append(
            f"📍 <b>{row['sinyal']}</b> | {trend_emoji} <b>{row['trend']}</b> | {fase_emoji} <b>{row['fase']}</b>"
        )
        lines.append(
            f"📊 Gain <b>{fmt_pct(row['gain'])}</b> | RSI <b>{rsi_cell_text(row['rsi'])}</b> | RSI 5M <b>{rsi_cell_text(row['rsi_5m'])}</b>"
        )
        lines.append("────────────")

    return "\n".join(lines)


def build_telegram_strong_alert_message(df: pd.DataFrame, top_n: int = 5):
    if df.empty:
        return "📭 <b>Tidak ada alert kuat</b>"

    scan_time = st.session_state.get("last_run", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    picked = df.head(top_n)
    lines = ["🚨 <b>ALERT KUAT</b>", f"🕒 <b>{scan_time}</b>", ""]

    for i, (_, row) in enumerate(picked.iterrows(), start=1):
        signal = str(row["sinyal"]).upper()
        trend = str(row["trend"]).upper()
        fase = str(row["fase"]).upper()

        if signal == "SUPER":
            signal_emoji = "🚀"
        elif signal in ["AKUM", "ON TRACK", "HAKA", "GC NOW"]:
            signal_emoji = "✅"
        elif signal == "REBOUND":
            signal_emoji = "🔄"
        elif signal in ["DIST", "WASPADA OB"]:
            signal_emoji = "⚠️"
        else:
            signal_emoji = "⏳"

        trend_emoji = "📈" if trend == "BULL" else "📉" if trend == "BEAR" else "➡️"
        fase_emoji = "🐂" if fase in ["AKUM", "BIG AKUM"] else "🐻" if fase in ["DIST", "BIG DIST"] else "⚪"

        lines.append(f"<b>{i}. {signal_emoji} {row['symbol']}</b>")
        lines.append(
            f"💰 <b>{fmt_price(row['now'])}</b> | "
            f"🎯 <b>{fmt_price(row['entry'])}</b> | "
            f"🏁 <b>{fmt_price(row['tp'])}</b> | "
            f"🛑 <b>{fmt_price(row['sl'])}</b>"
        )
        lines.append(
            f"🏆 Akum <b>{int(row['score_accum'])}</b> | "
            f"🧠 Total <b>{int(row['score_total'])}</b> | "
            f"⚡ RVOL <b>{fmt_pct(row['rvol'])}</b>"
        )
        lines.append(
            f"⚡ Scalp <b>{int(row['score_scalping'])}</b> | "
            f"🎯 BSJP <b>{int(row['score_bsjp'])}</b> | "
            f"📈 Swing <b>{int(row['score_swing'])}</b> | "
            f"🏦 Bandar <b>{int(row['score_bandar'])}</b>"
        )
        lines.append(
            f"📍 <b>{row['sinyal']}</b> | {trend_emoji} <b>{row['trend']}</b> | {fase_emoji} <b>{row['fase']}</b>"
        )
        lines.append(f"📊 Gain <b>{fmt_pct(row['gain'])}</b> | RSI <b>{rsi_cell_text(row['rsi'])}</b>")
        lines.append("────────────")

    return "\n".join(lines)


def build_telegram_alerts(df: pd.DataFrame):
    if df.empty:
        return pd.DataFrame()

    alert_df = df[
        (df["score_accum"] >= 60) &
        (df["rvol"] >= 150) &
        (df["sinyal"].isin(["SUPER", "ON TRACK", "AKUM", "HAKA"]))
    ].copy()

    return alert_df.sort_values(["score_accum", "score_total", "rvol", "gain"], ascending=[False, False, False, False]).reset_index(drop=True)


# =========================================================
# FINAL TELEGRAM BOX ENGINE — TOP SIGNAL + EMOJI + ANTI SPAM
# =========================================================
def signal_emoji(signal: str, gain=None) -> str:
    s = str(signal).upper()
    if s in ["SUPER", "ON TRACK", "AKUM", "HAKA", "GC NOW"]:
        return "🔥"
    if s == "REBOUND":
        return "🔄"
    if s in ["DIST", "WASPADA OB"]:
        return "⚠️"
    if s in ["DEAD", "BREAKDOWN", "EXIT"]:
        return "💀"
    if gain is not None and not pd.isna(gain):
        return "📈" if gain >= 0 else "📉"
    return "⏳"


def buy_sell_label(row) -> str:
    signal = str(row.get("sinyal", "")).upper()
    score_accum = row.get("score_accum", 0)
    score_total = row.get("score_total", 0)
    rvol = row.get("rvol", 0)
    trend = str(row.get("trend", "")).upper()
    rsi = row.get("rsi", np.nan)

    if signal in ["SUPER", "ON TRACK", "AKUM", "HAKA", "GC NOW"] and score_accum >= 65 and rvol >= 120:
        return "🔥 BUY / TOP SIGNAL"
    if signal == "REBOUND" and score_accum >= 55 and not pd.isna(rsi) and rsi < 45:
        return "🔄 BUY REBOUND"
    if signal in ["DIST", "WASPADA OB"] or trend == "BEAR":
        return "⚠️ SELL / AVOID"
    if score_accum >= 55 or score_total >= 8:
        return "👀 WATCH"
    return "⏳ WAIT"


def risk_label(score_accum, rsi, trend, signal) -> str:
    signal = str(signal).upper()
    trend = str(trend).upper()

    if signal in ["DIST", "WASPADA OB"] or trend == "BEAR":
        return "HIGH"
    if not pd.isna(rsi) and rsi >= 72:
        return "HIGH"
    if score_accum >= 70:
        return "LOW"
    if score_accum >= 50:
        return "MEDIUM"
    return "HIGH"


def momentum_label(row) -> str:
    score = row.get("score_total", 0)
    rvol = row.get("rvol", 0)
    rsi = row.get("rsi", np.nan)

    if score >= 10 and rvol >= 150 and not pd.isna(rsi) and 50 <= rsi <= 70:
        return "KUAT"
    if score >= 6:
        return "SEDANG"
    return "LEMAH"


def safe_text(value, default="-"):
    if value is None:
        return default
    try:
        if pd.isna(value):
            return default
    except Exception:
        pass
    return str(value)


def build_box_telegram_message(row, rank: int = 1):
    symbol = safe_text(row.get("symbol"))
    now = fmt_price(row.get("now", np.nan))
    gain = fmt_pct(row.get("gain", np.nan))
    rvol = fmt_pct(row.get("rvol", np.nan))
    value = human_value(row.get("val", np.nan))
    rsi = rsi_cell_text(row.get("rsi", np.nan))
    rsi5 = rsi_cell_text(row.get("rsi_5m", np.nan))

    trend = safe_text(row.get("trend"))
    fase = safe_text(row.get("fase"))
    sinyal = safe_text(row.get("sinyal"))
    aksi = safe_text(row.get("aksi"))
    rekomendasi = buy_sell_label(row)
    emoji = signal_emoji(sinyal, row.get("gain", np.nan))

    entry = fmt_price(row.get("entry", np.nan))
    sl = fmt_price(row.get("sl", np.nan))
    tp = fmt_price(row.get("tp", np.nan))
    profit = fmt_pct(row.get("profit", np.nan))
    to_tp = fmt_pct(row.get("to_tp", np.nan))

    arah = "▼" if not pd.isna(row.get("gain", np.nan)) and row.get("gain", 0) < 0 else "▲"
    score_accum = int(row.get("score_accum", 0))
    score_total = int(row.get("score_total", 0))
    score_bandar = int(row.get("score_bandar", 0))
    score_scalping = int(row.get("score_scalping", 0))
    risk = risk_label(score_accum, row.get("rsi", np.nan), trend, sinyal)
    momentum = momentum_label(row)

    message = f"""<pre>
┌──────────────────────────────────────────────┐
│ #{rank:<2} {emoji} {symbol:<6} | AI STOCK SCREENER        │
│ Harga : {now:<8} {arah} {gain:<10}           │
│ RVOL  : {rvol:<8} | Value : {value:<10}      │
├──────────────────────────────────────────────┤
│ Rekomendasi : {rekomendasi:<24}│
│ Aksi        : {aksi:<24}│
│ Trend       : {trend:<24}│
│ Fase        : {fase:<24}│
│ RSI / 5M    : {rsi:<8} / {rsi5:<13}│
├──────────────────────────────────────────────┤
│ AI Akum     : {score_accum:<24}│
│ AI Total    : {score_total:<24}│
│ Bandar      : {score_bandar:<24}│
│ Scalping    : {score_scalping:<24}│
│ Momentum    : {momentum:<24}│
│ Risiko      : {risk:<24}│
├──────────────────────────────────────────────┤
│ Sinyal      : {sinyal:<24}│
│ Entry       : {entry:<24}│
│ Stop Loss   : {sl:<24}│
│ Take Profit : {tp:<24}│
│ Profit      : {profit:<24}│
│ Sisa ke TP  : {to_tp:<24}│
└──────────────────────────────────────────────┘
</pre>"""
    return message


def get_top_signal_df(df: pd.DataFrame, top_n: int = 5):
    if df.empty:
        return pd.DataFrame()

    x = df.copy()
    strong_signals = ["SUPER", "ON TRACK", "AKUM", "HAKA", "GC NOW", "REBOUND"]

    x["telegram_rank_score"] = (
        x["score_accum"].fillna(0) * 2.0 +
        x["score_total"].fillna(0) * 3.0 +
        x["rvol"].fillna(0) * 0.08 +
        x["gain"].fillna(0) * 1.5 +
        x["sinyal"].isin(strong_signals).astype(int) * 25
    )

    # TOP SIGNAL: prioritas sinyal kuat, tapi tetap fallback ke ranking terbaik bila belum ada yang kuat.
    top_signal = x[
        (
            (x["score_accum"] >= 55) &
            (x["rvol"] >= 100) &
            (x["sinyal"].isin(strong_signals))
        ) |
        (
            (x["score_accum"] >= 70) &
            (x["score_total"] >= 8)
        )
    ].copy()

    if top_signal.empty:
        top_signal = x.copy()

    return top_signal.sort_values(
        ["telegram_rank_score", "score_accum", "score_total", "rvol", "gain"],
        ascending=[False, False, False, False, False]
    ).head(top_n).reset_index(drop=True)


def build_telegram_watchlist_message(df: pd.DataFrame, top_n: int = 5):
    if df.empty:
        return "📭 <b>Tidak ada saham yang lolos filter</b>"

    scan_time = st.session_state.get("last_run", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    picked = get_top_signal_df(df, top_n=top_n)

    header = f"🚨 <b>TOP {len(picked)} SIGNAL AI SCREENER</b>\n🕒 <b>{scan_time}</b>\n"
    boxes = [build_box_telegram_message(row, rank=i) for i, (_, row) in enumerate(picked.iterrows(), start=1)]
    return header + "\n" + "\n".join(boxes)


def build_telegram_strong_alert_message(df: pd.DataFrame, top_n: int = 5):
    if df.empty:
        return "📭 <b>Tidak ada alert kuat</b>"
    return build_telegram_watchlist_message(df, top_n=top_n)


def build_telegram_alerts(df: pd.DataFrame):
    return get_top_signal_df(df, top_n=5)

# =========================================================
# DATA SOURCE
# =========================================================
@st.cache_data(ttl=300)
def get_ohlcv(symbol: str, period: str = "6mo", interval: str = "1d") -> pd.DataFrame:
    try:
        df = yf.download(symbol, period=period, interval=interval, auto_adjust=False, progress=False, threads=False)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        if df.empty:
            return pd.DataFrame()
        required = ["Open", "High", "Low", "Close", "Volume"]
        for col in required:
            if col not in df.columns:
                return pd.DataFrame()
        return df.dropna(subset=["Open", "High", "Low", "Close"]).copy()
    except Exception:
        return pd.DataFrame()


@st.cache_data(ttl=300)
def get_intraday_5m(symbol: str) -> pd.DataFrame:
    try:
        df = yf.download(symbol, period="5d", interval="5m", auto_adjust=False, progress=False, threads=False)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        if df.empty:
            return pd.DataFrame()
        return df.dropna().copy()
    except Exception:
        return pd.DataFrame()

# =========================================================
# INDICATORS
# =========================================================
def calc_indicators(df: pd.DataFrame) -> pd.DataFrame:
    x = df.copy()
    x["MA5"] = x["Close"].rolling(5).mean()
    x["MA10"] = x["Close"].rolling(10).mean()
    x["MA20"] = x["Close"].rolling(20).mean()
    x["MA50"] = x["Close"].rolling(50).mean()
    x["EMA9"] = x["Close"].ewm(span=9, adjust=False).mean()
    x["EMA20"] = x["Close"].ewm(span=20, adjust=False).mean()

    delta = x["Close"].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(14).mean()
    avg_loss = loss.rolling(14).mean().replace(0, np.nan)
    rs = avg_gain / avg_loss
    x["RSI"] = 100 - (100 / (1 + rs))

    ema12 = x["Close"].ewm(span=12, adjust=False).mean()
    ema26 = x["Close"].ewm(span=26, adjust=False).mean()
    x["MACD"] = ema12 - ema26
    x["MACD_SIGNAL"] = x["MACD"].ewm(span=9, adjust=False).mean()
    x["MACD_HIST"] = x["MACD"] - x["MACD_SIGNAL"]

    x["BB_MID"] = x["Close"].rolling(20).mean()
    std20 = x["Close"].rolling(20).std()
    x["BB_UPPER"] = x["BB_MID"] + 2 * std20
    x["BB_LOWER"] = x["BB_MID"] - 2 * std20

    x["VOL_MA5"] = x["Volume"].rolling(5).mean()
    x["VOL_MA20"] = x["Volume"].rolling(20).mean()
    x["SUPPORT20"] = x["Low"].rolling(20).min()
    x["RESIST20"] = x["High"].rolling(20).max()

    high_low = x["High"] - x["Low"]
    high_close = np.abs(x["High"] - x["Close"].shift())
    low_close = np.abs(x["Low"] - x["Close"].shift())
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    x["ATR14"] = tr.rolling(14).mean()

    body = (x["Close"] - x["Open"]).abs()
    upper_wick = x["High"] - x[["Open", "Close"]].max(axis=1)
    lower_wick = x[["Open", "Close"]].min(axis=1) - x["Low"]
    candle_range = (x["High"] - x["Low"]).replace(0, np.nan)
    x["BODY"] = body
    x["UPPER_WICK"] = upper_wick.clip(lower=0)
    x["LOWER_WICK"] = lower_wick.clip(lower=0)
    x["WICK_PCT"] = ((x["UPPER_WICK"] + x["LOWER_WICK"]) / candle_range) * 100
    return x

# =========================================================
# SIGNAL ENGINE
# =========================================================
def get_phase(df: pd.DataFrame) -> str:
    recent = df.tail(10)
    score = 0
    for _, row in recent.iterrows():
        vol_ma20 = row.get("VOL_MA20", np.nan)
        if pd.isna(vol_ma20) or vol_ma20 <= 0:
            continue
        if row["Close"] > row["Open"] and row["Volume"] > vol_ma20:
            score += 1
        elif row["Close"] < row["Open"] and row["Volume"] > vol_ma20:
            score -= 1
    if score >= 4:
        return "BIG AKUM"
    if score >= 2:
        return "AKUM"
    if score <= -4:
        return "BIG DIST"
    if score <= -2:
        return "DIST"
    return "NEUTRAL"


def get_trend(close_, ma20, ma50) -> str:
    if pd.isna(close_) or pd.isna(ma20) or pd.isna(ma50):
        return "NEUTRAL"
    if close_ > ma20 > ma50:
        return "BULL"
    if close_ < ma20 < ma50:
        return "BEAR"
    return "NEUTRAL"


def get_rsi_signal(rsi, macd, macd_signal) -> str:
    if pd.isna(rsi) or pd.isna(macd) or pd.isna(macd_signal):
        return "WAIT"
    if 48 <= rsi <= 55 and macd > macd_signal:
        return "GOLDEN"
    if rsi >= 58 and macd > macd_signal:
        return "UP"
    if rsi <= 42 and macd < macd_signal:
        return "DEAD"
    return "UP" if rsi >= 50 else "DEAD"


def get_signal_label(close_, ma20, ma50, ema9, rsi, macd, macd_signal, vol, vol_ma20, support, resistance, wick):
    if any(pd.isna(v) for v in [close_, ma20, ema9, rsi, macd, macd_signal]):
        return "WAIT"

    bullish = macd > macd_signal
    near_support = not pd.isna(support) and close_ <= support * 1.04
    near_resistance = not pd.isna(resistance) and close_ >= resistance * 0.985
    vol_ok = not pd.isna(vol_ma20) and vol > vol_ma20
    trend_bull = not pd.isna(ma50) and close_ > ma20 > ma50

    if bullish and vol_ok and near_resistance and rsi >= 58:
        return "ON TRACK"
    if bullish and close_ > ema9 > ma20 and rsi >= 62 and vol_ok:
        return "SUPER"
    if bullish and near_support and rsi < 42:
        return "REBOUND"
    if bullish and vol_ok and close_ > ma20:
        return "AKUM"
    if trend_bull and 50 <= rsi <= 60 and wick < 35:
        return "HAKA"
    if rsi >= 72 and wick >= 35:
        return "WASPADA OB"
    if close_ < ma20 and not bullish and rsi < 45:
        return "DIST"
    if 47 <= rsi <= 54 and bullish:
        return "GC NOW"
    return "WAIT"


def get_action_label(signal_label, close_, entry, trend):
    if signal_label in ["ON TRACK", "AKUM", "HAKA", "GC NOW", "REBOUND"]:
        if not pd.isna(entry) and close_ <= entry * 1.02:
            return "AT ENTRY"
        return "WATCH"
    if signal_label == "SUPER":
        return "SIAP BELI"
    if signal_label == "WASPADA OB":
        return "WASPADA OB"
    if trend == "BULL":
        return "HOLD"
    return "WAIT GC"


def compute_scores(df: pd.DataFrame):
    close_ = latest(df["Close"])
    ma20 = latest(df["MA20"])
    ma50 = latest(df["MA50"])
    ema9 = latest(df["EMA9"])
    rsi = latest(df["RSI"])
    macd = latest(df["MACD"])
    macd_signal = latest(df["MACD_SIGNAL"])
    volume = latest(df["Volume"])
    vol_ma5 = latest(df["VOL_MA5"])
    vol_ma20 = latest(df["VOL_MA20"])
    support = latest(df["SUPPORT20"])
    resistance = latest(df["RESIST20"])
    bb_lower = latest(df["BB_LOWER"])
    wick = latest(df["WICK_PCT"])

    scalping = 0
    if close_ > ema9 > ma20:
        scalping += 3
    if 55 <= rsi <= 72:
        scalping += 2
    if macd > macd_signal:
        scalping += 2
    if not pd.isna(vol_ma5) and volume > vol_ma5:
        scalping += 2
    if not pd.isna(resistance) and close_ >= resistance * 0.985:
        scalping += 1
    if not pd.isna(wick) and wick < 35:
        scalping += 1

    bsjp = 0
    if not pd.isna(rsi):
        if rsi < 35:
            bsjp += 3
        elif 35 <= rsi <= 45:
            bsjp += 1
    if not pd.isna(bb_lower) and close_ <= bb_lower * 1.03:
        bsjp += 2
    if not pd.isna(support) and close_ <= support * 1.05:
        bsjp += 2
    if len(df) > 1 and df["Close"].iloc[-1] > df["Close"].iloc[-2]:
        bsjp += 1
    if df["MACD_HIST"].iloc[-1] > 0:
        bsjp += 2

    swing = 0
    if close_ > ma20 > ma50:
        swing += 3
    if 50 <= rsi <= 65:
        swing += 2
    if macd > macd_signal:
        swing += 2
    if not pd.isna(vol_ma20) and volume > vol_ma20:
        swing += 1
    if (not pd.isna(resistance)) and (not pd.isna(support)):
        if close_ < resistance * 0.93 and close_ > support * 1.08:
            swing += 1

    bandar = 0
    phase = get_phase(df)
    if phase == "BIG AKUM":
        bandar += 4
    elif phase == "AKUM":
        bandar += 2
    elif phase == "DIST":
        bandar -= 2
    elif phase == "BIG DIST":
        bandar -= 4
    if not pd.isna(vol_ma20) and vol_ma20 > 0 and volume > vol_ma20 * 1.2:
        bandar += 2
    if close_ > ma20:
        bandar += 1

    return {"scalping": scalping, "bsjp": bsjp, "swing": swing, "bandar": bandar}


def compute_accum_score(close_, ma20, ma50, rsi, rvol, val, phase, signal, gain):
    score = 0
    if not pd.isna(rvol):
        if rvol >= 250:
            score += 30
        elif rvol >= 180:
            score += 24
        elif rvol >= 120:
            score += 18
        elif rvol >= 100:
            score += 10
    if not pd.isna(val):
        if val >= 100_000_000_000:
            score += 20
        elif val >= 50_000_000_000:
            score += 15
        elif val >= 20_000_000_000:
            score += 10
        elif val >= 10_000_000_000:
            score += 6
    if not pd.isna(close_) and not pd.isna(ma20) and close_ > ma20:
        score += 8
    if not pd.isna(ma20) and not pd.isna(ma50) and ma20 > ma50:
        score += 8
    if not pd.isna(rsi):
        if 52 <= rsi <= 68:
            score += 10
        elif 45 <= rsi < 52:
            score += 5
    if phase == "BIG AKUM":
        score += 15
    elif phase == "AKUM":
        score += 10
    elif phase == "DIST":
        score -= 8
    elif phase == "BIG DIST":
        score -= 15
    if signal in ["SUPER", "ON TRACK", "AKUM", "HAKA"]:
        score += 10
    if not pd.isna(gain):
        if gain > 0:
            score += 4
        elif gain < -3:
            score -= 5
    return max(score, 0)

# =========================================================
# ROW BUILDER
# =========================================================
def build_row(symbol: str, daily_df: pd.DataFrame, intraday_5m: pd.DataFrame):
    df = calc_indicators(daily_df)
    if len(df) < 30:
        return None

    close_ = latest(df["Close"])
    prev_close = float(df["Close"].iloc[-2]) if len(df) > 1 else close_
    gain = ((close_ - prev_close) / prev_close * 100) if prev_close else 0.0
    wick = latest(df["WICK_PCT"])
    rsi = latest(df["RSI"])
    macd = latest(df["MACD"])
    macd_signal = latest(df["MACD_SIGNAL"])
    vol = latest(df["Volume"])
    vol_ma20 = latest(df["VOL_MA20"])
    ma20 = latest(df["MA20"])
    ma50 = latest(df["MA50"])
    ema9 = latest(df["EMA9"])
    support = latest(df["SUPPORT20"])
    resistance = latest(df["RESIST20"])
    atr = latest(df["ATR14"])

    rvol = (vol / vol_ma20 * 100) if not pd.isna(vol_ma20) and vol_ma20 > 0 else np.nan
    entry = round((support + ma20) / 2) if not pd.isna(support) and not pd.isna(ma20) else round(close_)
    now_price = close_
    tp = round(close_ + (atr * 2)) if not pd.isna(atr) else round(close_ * 1.04)
    sl = round(close_ - atr) if not pd.isna(atr) else round(close_ * 0.97)
    profit = ((now_price - entry) / entry * 100) if entry else 0.0
    to_tp = ((tp - now_price) / now_price * 100) if now_price else 0.0

    intraday_rsi = np.nan
    if not intraday_5m.empty and "Close" in intraday_5m.columns:
        intra = calc_indicators(intraday_5m)
        intraday_rsi = latest(intra["RSI"])

    trend = get_trend(close_, ma20, ma50)
    phase = get_phase(df)
    rsi_sig = get_rsi_signal(rsi, macd, macd_signal)
    sinyal = get_signal_label(close_, ma20, ma50, ema9, rsi, macd, macd_signal, vol, vol_ma20, support, resistance, wick)
    aksi = get_action_label(sinyal, close_, entry, trend)
    val = close_ * vol if not pd.isna(close_) and not pd.isna(vol) else np.nan

    scores = compute_scores(df)
    total = scores["scalping"] + scores["bsjp"] + scores["swing"] + scores["bandar"]
    accum_score = compute_accum_score(close_, ma20, ma50, rsi, rvol, val, phase, sinyal, gain)

    return {
        "symbol": symbol.replace(".JK", ""),
        "full_symbol": symbol,
        "gain": gain,
        "wick": wick,
        "aksi": aksi,
        "sinyal": sinyal,
        "rvol": rvol,
        "entry": entry,
        "now": now_price,
        "tp": tp,
        "sl": sl,
        "profit": profit,
        "to_tp": to_tp,
        "rsi": rsi,
        "rsi_sig": rsi_sig,
        "rsi_5m": intraday_rsi,
        "val": val,
        "fase": phase,
        "trend": trend,
        "score_scalping": scores["scalping"],
        "score_bsjp": scores["bsjp"],
        "score_swing": scores["swing"],
        "score_bandar": scores["bandar"],
        "score_total": total,
        "score_accum": accum_score,
        "daily_df": df
    }


@st.cache_data(ttl=300)
def run_screener(symbols, period, interval, max_price=1000):
    rows = []
    for symbol in symbols:
        try:
            daily = get_ohlcv(symbol, period=period, interval=interval)
            if daily.empty:
                continue
            intra5 = get_intraday_5m(symbol)
            row = build_row(symbol, daily, intra5)
            if row is not None and not pd.isna(row["now"]) and row["now"] <= max_price:
                rows.append(row)
        except Exception:
            continue
    if not rows:
        return pd.DataFrame()
    return pd.DataFrame(rows).sort_values(["score_accum", "score_total", "rvol", "gain"], ascending=[False, False, False, False]).reset_index(drop=True)

# =========================================================
# CELL COLORS
# =========================================================
def bg_gain(v):
    if pd.isna(v):
        return "#243244"
    if v > 3:
        return "#10b981"
    if v > 0:
        return "#15803d"
    if v > -2:
        return "#dc2626"
    return "#991b1b"


def bg_wick(v):
    if pd.isna(v):
        return "#243244"
    if v < 15:
        return "#0f766e"
    if v < 25:
        return "#2563eb"
    if v < 35:
        return "#d97706"
    return "#dc2626"


def bg_aksi(v):
    mapping = {"AT ENTRY": "#1d4ed8", "WATCH": "#b45309", "WAIT GC": "#374151", "HOLD": "#2563eb", "SIAP BELI": "#7c3aed", "WASPADA OB": "#d97706"}
    return mapping.get(v, "#334155")


def bg_sinyal(v):
    mapping = {"ON TRACK": "#16a34a", "REBOUND": "#d97706", "AKUM": "#15803d", "DIST": "#b91c1c", "SUPER": "#7e22ce", "HAKA": "#14b8a6", "GC NOW": "#9333ea", "WASPADA OB": "#ea580c", "WAIT": "#111827"}
    return mapping.get(v, "#334155")


def bg_rvol(v):
    if pd.isna(v):
        return "#243244"
    if v >= 250:
        return "#9333ea"
    if v >= 150:
        return "#f97316"
    if v >= 100:
        return "#2563eb"
    return "#374151"


def bg_price(kind):
    mapping = {"entry": "#1d4ed8", "now": "#2563eb", "tp": "#16a34a", "sl": "#b91c1c"}
    return mapping.get(kind, "#243244")


def bg_profit(v):
    if pd.isna(v):
        return "#243244"
    if v > 2:
        return "#16a34a"
    if v > 0:
        return "#0f766e"
    if v > -2:
        return "#92400e"
    return "#b91c1c"


def bg_to_tp(v):
    if pd.isna(v):
        return "#243244"
    if v <= 1:
        return "#f97316"
    if v <= 3:
        return "#16a34a"
    return "#0f766e"


def bg_rsi_sig(v):
    mapping = {"UP": "#16a34a", "DEAD": "#dc2626", "GOLDEN": "#7c3aed", "WAIT": "#111827"}
    return mapping.get(v, "#334155")


def bg_rsi(v):
    if pd.isna(v):
        return "#243244"
    if v >= 70:
        return "#f59e0b"
    if v >= 55:
        return "#16a34a"
    if v >= 45:
        return "#2563eb"
    return "#7c3aed"


def bg_fase(v):
    mapping = {"BIG AKUM": "#9333ea", "AKUM": "#16a34a", "NEUTRAL": "#374151", "DIST": "#dc2626", "BIG DIST": "#991b1b"}
    return mapping.get(v, "#334155")


def bg_trend(v):
    mapping = {"BULL": "#16a34a", "BEAR": "#dc2626", "NEUTRAL": "#6b7280"}
    return mapping.get(v, "#334155")


def bg_accum_score(v):
    if pd.isna(v):
        return "#243244"
    if v >= 70:
        return "#9333ea"
    if v >= 55:
        return "#16a34a"
    if v >= 40:
        return "#2563eb"
    return "#374151"

# =========================================================
# HTML TABLE
# =========================================================
def make_html_table(df: pd.DataFrame, title: str, sub: str):
    html = textwrap.dedent(f"""
    <html>
    <head>
    <style>
    body {{
        margin: 0;
        background: #07111b;
        color: white;
        font-family: Arial, Helvetica, sans-serif;
    }}
    .screen-box {{
        border: 1px solid #17324d;
        border-radius: 10px;
        padding: 8px;
        background: #07111b;
        box-sizing: border-box;
        width: 100%;
    }}
    .screener-title {{
        text-align: center;
        font-weight: 800;
        font-size: 13px;
        color: #eaf2ff;
        margin-bottom: 4px;
        letter-spacing: 0.3px;
    }}
    .screener-sub {{
        text-align: center;
        color: #9fb5d1;
        font-size: 10px;
        margin-bottom: 6px;
    }}
    .table-wrap {{
        width: 100%;
        overflow-x: auto;
    }}
    .custom-table {{
        width: 100%;
        border-collapse: collapse;
        font-size: 11px;
        min-width: 1500px;
    }}
    .custom-table th {{
        background: #184574;
        color: #ffffff;
        border: 1px solid #2a527b;
        padding: 5px 3px;
        text-align: center;
        white-space: nowrap;
        font-weight: 800;
    }}
    .custom-table td {{
        border: 1px solid #20364e;
        padding: 4px 3px;
        text-align: center;
        white-space: nowrap;
        font-weight: 700;
    }}
    .footer-line {{
        margin-top: 6px;
        text-align: center;
        color: #ffd451;
        font-size: 10px;
        font-weight: 700;
    }}
    </style>
    </head>
    <body>
    <div class="screen-box">
      <div class="screener-title">{title}</div>
      <div class="screener-sub">{sub}</div>
      <div class="table-wrap">
      <table class="custom-table">
        <thead>
          <tr>
            <th>RANK</th>
            <th>EMITEN</th>
            <th>AKUM SCORE</th>
            <th>TOTAL</th>
            <th>GAIN</th>
            <th>WICK</th>
            <th>AKSI</th>
            <th>SINYAL</th>
            <th>RVOL</th>
            <th>ENTRY</th>
            <th>NOW</th>
            <th>TP</th>
            <th>SL</th>
            <th>PROFIT</th>
            <th>%TO TP</th>
            <th>RSI SIG</th>
            <th>RSI</th>
            <th>RSI 5M</th>
            <th>VAL</th>
            <th>FASE</th>
            <th>TREND</th>
          </tr>
        </thead>
        <tbody>
    """)

    for i, (_, row) in enumerate(df.iterrows(), start=1):
        html += f"""
        <tr>
            <td style="background:#0f172a;color:#fff;">{i}</td>
            <td style="background:#1d4ed8;color:#fff;">{row['symbol']}</td>
            <td style="background:{bg_accum_score(row['score_accum'])};color:#fff;">{int(row['score_accum'])}</td>
            <td style="background:#0b3b66;color:#fff;">{int(row['score_total'])}</td>
            <td style="background:{bg_gain(row['gain'])};color:#fff;">{fmt_pct(row['gain'])}</td>
            <td style="background:{bg_wick(row['wick'])};color:#fff;">{fmt_pct(row['wick'])}</td>
            <td style="background:{bg_aksi(row['aksi'])};color:#fff;">{row['aksi']}</td>
            <td style="background:{bg_sinyal(row['sinyal'])};color:#fff;">{row['sinyal']}</td>
            <td style="background:{bg_rvol(row['rvol'])};color:#fff;">{fmt_pct(row['rvol'])}</td>
            <td style="background:{bg_price('entry')};color:#fff;">{fmt_price(row['entry'])}</td>
            <td style="background:{bg_price('now')};color:#fff;">{fmt_price(row['now'])}</td>
            <td style="background:{bg_price('tp')};color:#fff;">{fmt_price(row['tp'])}</td>
            <td style="background:{bg_price('sl')};color:#fff;">{fmt_price(row['sl'])}</td>
            <td style="background:{bg_profit(row['profit'])};color:#fff;">{fmt_pct(row['profit'])}</td>
            <td style="background:{bg_to_tp(row['to_tp'])};color:#fff;">{fmt_pct(row['to_tp'])}</td>
            <td style="background:{bg_rsi_sig(row['rsi_sig'])};color:#fff;">{row['rsi_sig']}</td>
            <td style="background:{bg_rsi(row['rsi'])};color:#fff;">{rsi_cell_text(row['rsi'])}</td>
            <td style="background:{bg_rsi(row['rsi_5m'])};color:#fff;">{rsi_cell_text(row['rsi_5m'])}</td>
            <td style="background:#183b69;color:#fff;">{human_value(row['val'])}</td>
            <td style="background:{bg_fase(row['fase'])};color:#fff;">{row['fase']}</td>
            <td style="background:{bg_trend(row['trend'])};color:#fff;">{row['trend']}</td>
        </tr>
        """

    html += """
        </tbody>
      </table>
      </div>
      <div class="footer-line">Top 30 | fokus akumulasi + RVOL | SL≈1xATR | TP≈2xATR | filter harga ≤ 1000 | yfinance mode</div>
    </div>
    </body>
    </html>
    """
    return html

# =========================================================
# CHART DETAIL
# =========================================================
def show_detail_chart(df: pd.DataFrame, symbol_name: str):
    st.subheader(f"Chart Detail: {symbol_name}")

    fig = go.Figure()
    fig.add_trace(go.Candlestick(x=df.index, open=df["Open"], high=df["High"], low=df["Low"], close=df["Close"], name="Candlestick"))
    fig.add_trace(go.Scatter(x=df.index, y=df["MA20"], mode="lines", name="MA20"))
    fig.add_trace(go.Scatter(x=df.index, y=df["MA50"], mode="lines", name="MA50"))
    fig.add_trace(go.Scatter(x=df.index, y=df["BB_UPPER"], mode="lines", name="BB Upper"))
    fig.add_trace(go.Scatter(x=df.index, y=df["BB_LOWER"], mode="lines", name="BB Lower"))
    fig.update_layout(height=520, template="plotly_dark", xaxis_rangeslider_visible=False, margin=dict(l=20, r=20, t=40, b=20))
    st.plotly_chart(fig, use_container_width=True)

    c1, c2 = st.columns(2)
    with c1:
        fig_rsi = go.Figure()
        fig_rsi.add_trace(go.Scatter(x=df.index, y=df["RSI"], mode="lines", name="RSI"))
        fig_rsi.add_hline(y=70, line_dash="dash")
        fig_rsi.add_hline(y=30, line_dash="dash")
        fig_rsi.update_layout(height=280, template="plotly_dark", title="RSI")
        st.plotly_chart(fig_rsi, use_container_width=True)
    with c2:
        fig_macd = go.Figure()
        fig_macd.add_trace(go.Scatter(x=df.index, y=df["MACD"], mode="lines", name="MACD"))
        fig_macd.add_trace(go.Scatter(x=df.index, y=df["MACD_SIGNAL"], mode="lines", name="Signal"))
        fig_macd.add_trace(go.Bar(x=df.index, y=df["MACD_HIST"], name="Histogram"))
        fig_macd.update_layout(height=280, template="plotly_dark", title="MACD")
        st.plotly_chart(fig_macd, use_container_width=True)

# =========================================================
# HEADER
# =========================================================
st.title("HIGH PROB SCREENER FINAL — TOP SIGNAL + TELEGRAM")
st.markdown('<div class="small-note">fokus saham akumulasi + RVOL tinggi | ranking 30 terbaik | harga maksimal 1000 | auto refresh + telegram bot</div>', unsafe_allow_html=True)

# =========================================================
# SIDEBAR
# =========================================================
with st.sidebar:
    st.header("Pengaturan Final Screener")

    watchlist_name = st.selectbox("Preset Watchlist", list(WATCHLISTS.keys()), index=0)
    period = st.selectbox("Periode", ["3mo", "6mo", "1y", "2y"], index=1)
    interval = st.selectbox("Interval", ["1d", "1wk"], index=0)
    auto_refresh = st.checkbox("Auto Refresh", value=False)
    refresh_sec = st.selectbox("Refresh tiap", [30, 60, 120, 300], index=1)

    default_symbols_text = ",".join(WATCHLISTS[watchlist_name]) if watchlist_name != "Custom" else ""
    custom_symbols = st.text_area("Daftar saham watchlist (pisahkan koma)", value=default_symbols_text, height=160)

    st.markdown("---")
    st.subheader("Telegram Bot")
    telegram_enabled = st.checkbox("Aktifkan notifikasi Telegram", value=False)
    telegram_bot_token = st.text_input("Bot Token", type="password")
    telegram_chat_id = st.text_input("Chat ID")
    telegram_top_n = st.number_input("Kirim Top N", min_value=1, max_value=30, value=5, step=1)
    send_only_alerts = st.checkbox("Kirim hanya TOP SIGNAL", value=True)
    send_test_btn = st.button("Tes Kirim Telegram", use_container_width=True)

    if send_test_btn:
        now_text = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        test_message = (
    "🤖 <b>Test Notifikasi Berhasil</b>\n"
    "✅ Bot Telegram sudah terhubung ke screener.\n\n"
    f"🕒 <b>Waktu:</b> {now_text}\n"
    "📡 <b>Status:</b> ONLINE\n"
    "🔥 Sistem siap mengirim alert saham."
)
        ok, msg = send_telegram_message(telegram_bot_token, telegram_chat_id, test_message)
        if ok:
            st.success("Pesan test berhasil dikirim.")
        else:
            st.error(f"Gagal kirim test: {msg}")

    st.markdown("---")
    st.subheader("Search Emiten Mandiri")
    single_symbol = st.text_input("Masukkan emiten", placeholder="Contoh: BBCA atau GOTO")
    add_mode = st.radio("Mode pencarian", ["Tambahkan ke watchlist", "Analisa emiten ini saja"], index=0)
    run_btn = st.button("Jalankan Screener", use_container_width=True)

    st.markdown("---")
    st.info(f"Filter aktif: harga saham maksimal {MAX_PRICE}")
    st.info(f"Hasil utama dibatasi ke {TOP_N} saham terbaik")

# =========================================================
# PARSE SYMBOLS
# =========================================================
watchlist_symbols = [normalize_jk_symbol(x) for x in custom_symbols.split(",") if x.strip()]
watchlist_symbols = [x for x in watchlist_symbols if x]
manual_symbol = normalize_jk_symbol(single_symbol) if single_symbol else ""

if add_mode == "Tambahkan ke watchlist":
    symbols = watchlist_symbols.copy()
    if manual_symbol and manual_symbol not in symbols:
        symbols.append(manual_symbol)
else:
    symbols = [manual_symbol] if manual_symbol else []

symbols = list(dict.fromkeys(symbols))
if not symbols:
    st.warning("Masukkan minimal 1 kode saham atau cari 1 emiten.")
    st.stop()

# =========================================================
# RUN
# =========================================================
if run_btn or "screener_df" not in st.session_state:
    with st.spinner("Mengambil data dan menyusun screener..."):
        st.session_state["screener_df"] = run_screener(symbols, period, interval, max_price=MAX_PRICE)
        st.session_state["last_run"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

screener_df = st.session_state.get("screener_df", pd.DataFrame())
if screener_df.empty:
    st.error(f"Tidak ada data yang lolos filter. Pastikan kode emiten benar atau harga saham ≤ {MAX_PRICE}.")
    st.stop()

display_df = screener_df.sort_values(by=["score_accum", "score_total", "rvol", "gain"], ascending=[False, False, False, False]).head(TOP_N).reset_index(drop=True)
alert_df = build_telegram_alerts(display_df)

# =========================================================
# AUTO TELEGRAM NOTIF (ANTI SPAM)
# =========================================================
if telegram_enabled and auto_refresh and telegram_bot_token and telegram_chat_id and not display_df.empty:
    source_df = get_top_signal_df(display_df, top_n=int(telegram_top_n)) if send_only_alerts else display_df.head(int(telegram_top_n))
    current_alert_key = "|".join([f"{row['symbol']}-{int(row['score_accum'])}-{row['sinyal']}" for _, row in source_df.iterrows()])
    last_alert_key = st.session_state.get("last_alert_key", "")

    if current_alert_key != last_alert_key:
        if send_only_alerts:
            message = build_telegram_strong_alert_message(source_df, top_n=int(telegram_top_n))
        else:
            message = build_telegram_watchlist_message(source_df, top_n=int(telegram_top_n))

        ok, msg = send_telegram_message(telegram_bot_token, telegram_chat_id, message)
        if ok:
            st.session_state["last_alert_key"] = current_alert_key
            st.success("Auto notif Telegram terkirim")
        else:
            st.warning(f"Gagal auto notif: {msg}")

# =========================================================
# TOP METRICS
# =========================================================
top_symbol = display_df.iloc[0]["symbol"]
top_accum = int(display_df.iloc[0]["score_accum"])
top_score = int(display_df.iloc[0]["score_total"])
top_signal = display_df.iloc[0]["sinyal"]
last_run = st.session_state.get("last_run", "-")

m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("TOP PICK", top_symbol)
m2.metric("AKUM SCORE", top_accum)
m3.metric("TOTAL SCORE", top_score)
m4.metric("SIGNAL", top_signal)
m5.metric("LAST SCAN", last_run)

cbtn1, cbtn2 = st.columns(2)
with cbtn1:
    send_now_btn = st.button("Kirim Notifikasi Telegram", use_container_width=True)
with cbtn2:
    st.metric("Jumlah Alert Kuat", len(alert_df))

# =========================================================
# KIRIM MANUAL
# =========================================================
if telegram_enabled and send_now_btn:
    if send_only_alerts:
        target_df = get_top_signal_df(display_df, top_n=int(telegram_top_n))
        message = build_telegram_strong_alert_message(target_df, top_n=int(telegram_top_n))
    else:
        target_df = display_df.head(int(telegram_top_n))
        message = build_telegram_watchlist_message(target_df, top_n=int(telegram_top_n))

    ok, msg = send_telegram_message(telegram_bot_token, telegram_chat_id, message)
    if ok:
        st.success(f"TOP {int(telegram_top_n)} SIGNAL berhasil dikirim ke Telegram.")
    else:
        st.error(f"Gagal kirim Telegram: {msg}")

# =========================================================
# MAIN TABLE
# =========================================================
st.subheader("Top 30 Saham Akumulasi")
components.html(
    make_html_table(display_df, "HIGH PROB SCREENER V2.0 — TOP 30 AKUMULASI", "Ranking berdasarkan Akum Score + Total Score + RVOL + Gain"),
    height=560,
    scrolling=True
)

# =========================================================
# ALERT TABLE
# =========================================================
st.subheader("🚨 TOP SIGNAL Telegram")
if alert_df.empty:
    st.info("Belum ada saham dengan kriteria akumulasi kuat.")
else:
    st.dataframe(
        alert_df[["symbol", "now", "gain", "rvol", "rsi", "fase", "trend", "sinyal", "score_accum", "score_total"]],
        use_container_width=True,
        height=260
    )

# =========================================================
# RANKING TABLE
# =========================================================
st.subheader("Ranking 30 Data Terbaik")
rank_df = display_df[["symbol", "now", "gain", "rvol", "rsi", "rsi_5m", "val", "fase", "trend", "score_accum", "score_scalping", "score_bsjp", "score_swing", "score_bandar", "score_total"]].copy()
rank_df.columns = ["EMITEN", "PRICE", "GAIN", "RVOL", "RSI", "RSI 5M", "VALUE", "FASE", "TREND", "AKUM SCORE", "SCALPING", "BSJP", "SWING", "BANDAR", "TOTAL"]
rank_df["PRICE"] = rank_df["PRICE"].apply(fmt_price)
rank_df["GAIN"] = rank_df["GAIN"].apply(fmt_pct)
rank_df["RVOL"] = rank_df["RVOL"].apply(fmt_pct)
rank_df["RSI"] = rank_df["RSI"].apply(rsi_cell_text)
rank_df["RSI 5M"] = rank_df["RSI 5M"].apply(rsi_cell_text)
rank_df["VALUE"] = rank_df["VALUE"].apply(human_value)
st.dataframe(rank_df, use_container_width=True, height=520)

# =========================================================
# DETAIL PANEL
# =========================================================
selected_symbol = st.selectbox("Pilih saham untuk detail", display_df["full_symbol"].tolist())
selected_row = display_df[display_df["full_symbol"] == selected_symbol].iloc[0]
selected_df = selected_row["daily_df"]

d1, d2, d3, d4, d5, d6 = st.columns(6)
d1.metric("EMITEN", selected_row["symbol"])
d2.metric("PRICE", fmt_price(selected_row["now"]))
d3.metric("GAIN", fmt_pct(selected_row["gain"]))
d4.metric("RVOL", fmt_pct(selected_row["rvol"]))
d5.metric("AKUM SCORE", int(selected_row["score_accum"]))
d6.metric("RSI 5M", rsi_cell_text(selected_row["rsi_5m"]))

show_detail_chart(selected_df, selected_row["symbol"])

st.subheader("Analisa Strategi")
t1, t2, t3, t4 = st.tabs(["1. Scalping", "2. BSJP", "3. Swing", "4. Bandarmologi"])

with t1:
    st.write("Logika: mencari momentum cepat, price di atas EMA9/MA20, RVOL aktif, RSI sehat, dekat breakout.")
    st.metric("Skor Scalping", int(selected_row["score_scalping"]))
    st.write(f"Aksi: **{selected_row['aksi']}**")
    st.write(f"Sinyal: **{selected_row['sinyal']}**")
    st.write(f"Entry: **{fmt_price(selected_row['entry'])}**")
    st.write(f"TP: **{fmt_price(selected_row['tp'])}**")
    st.write(f"SL: **{fmt_price(selected_row['sl'])}**")

with t2:
    st.write("Logika: buy saat jenuh penurunan, dekat support atau lower band, lalu muncul tanda rebound.")
    st.metric("Skor BSJP", int(selected_row["score_bsjp"]))
    st.write(f"RSI: **{rsi_cell_text(selected_row['rsi'])}**")
    st.write(f"RSI 5M: **{rsi_cell_text(selected_row['rsi_5m'])}**")
    st.write(f"Fase: **{selected_row['fase']}**")

with t3:
    st.write("Logika: mengikuti tren menengah dengan konfirmasi MA20/MA50, MACD, volume, dan posisi harga.")
    st.metric("Skor Swing", int(selected_row["score_swing"]))
    st.write(f"Trend: **{selected_row['trend']}**")
    st.write(f"% To TP: **{fmt_pct(selected_row['to_tp'])}**")

with t4:
    st.write("Logika: proxy bandarmologi dari price-volume. Ini bukan broker summary asli, tapi pendekatan akumulasi/distribusi.")
    st.metric("Skor Bandarmologi", int(selected_row["score_bandar"]))
    st.write(f"Fase: **{selected_row['fase']}**")
    st.write(f"Value transaksi: **{human_value(selected_row['val'])}**")
    st.write(f"Akum Score: **{int(selected_row['score_accum'])}**")

st.caption("Catatan: data saat ini memakai yfinance. Broker summary, foreign flow, dan orderbook belum tersedia di versi ini.")

# =========================================================
# AUTO REFRESH
# =========================================================
if auto_refresh:
    auto_refresh_fragment(refresh_sec)
