import time
import requests
import textwrap
from datetime import datetime
from zoneinfo import ZoneInfo

WIB = ZoneInfo("Asia/Jakarta")

import numpy as np
import pandas as pd
import streamlit as st
import yfinance as yf
import streamlit.components.v1 as components


# =========================================================
# CONFIG
# =========================================================
st.set_page_config(page_title="IDX AI Screener + Telegram", layout="wide")

SYMBOLS = ["AALI", "ABBA", "ABDA", "ABMM", "ACES", "ACST", "ADCP", "ADES", "ADHI", "ADMF", "ADMG", "ADMR", "ADRO", "AGAR", "AGII", "AGRO", "AGRS", "AHAP", "AIMS", "AISA", "AKKU", "AKPI", "AKRA", "AKSI", "ALDO", "ALKA", "ALMI", "ALTO", "AMAG", "AMAR", "AMFG", "AMIN", "AMMN", "AMOR", "AMRT", "ANDI", "ANJT", "ANTM", "APEX", "APIC", "APII", "APLI", "APLN", "ARCI", "ARGO", "ARKA", "ARMY", "ARTA", "ARTI", "ASBI", "ASDM", "ASGR", "ASII", "ASJT", "ASMI", "ASRI", "ASRM", "ASSA", "ATAP", "ATIC", "AUTO", "AVIA", "AXIO", "BACA", "BAJA", "BALI", "BANK", "BAPA", "BAPI", "BATA", "BBCA", "BBHI", "BBKP", "BBLD", "BBMD", "BBNI", "BBRI", "BBTN", "BBYB", "BCAP", "BCIC", "BCIP", "BDMN", "BEKS", "BEST", "BFIN", "BHAT", "BHIT", "BIKA", "BIMA", "BINA", "BIPI", "BJBR", "BJTM", "BKDP", "BKSL", "BLTA", "BLUE", "BMAS", "BMRI", "BMSR", "BMTR", "BNBA", "BNBR", "BNGA", "BNII", "BNLI", "BOLA", "BOSS", "BPFI", "BPII", "BRAM", "BRIS", "BRMS", "BRNA", "BRPT", "BSDE", "BSSR", "BTEL", "BTON", "BTPN", "BTPS", "BUKA", "BULL", "BUMI", "BUVA", "BVIC", "CAMP", "CANI", "CARE", "CARS", "CBMF", "CBUT", "CCSI", "CEKA", "CENT", "CFIN", "CGAS", "CHEM", "CINT", "CITA", "CITY", "CLAY", "CLEO", "CMNP", "CMRY", "CNKO", "CNMA", "COAL", "CODE", "CPIN", "CPRO", "CSAP", "CSIS", "CTBN", "CTRA", "CTTH", "CUAN", "DADA", "DART", "DAYA", "DEAL", "DEFI", "DEPO", "DEWA", "DGIK", "DILD", "DKFT", "DLTA", "DMAS", "DNAR", "DOID", "DPNS", "DSFI", "DSNG", "DSSA", "DUTI", "DVLA", "EDGE", "EKAD", "ELSA", "EMDE", "EMTK", "ENAK", "ENRG", "ENVY", "EPAC", "ERAA", "ESSA", "ESTA", "ETWA", "FAPA", "FASW", "FILM", "FINN", "FIRE", "FISH", "FLMC", "FMII", "FPNI", "FREN", "GAMA", "GDST", "GEMS", "GGRM", "GIAA", "GJTL", "GLVA", "GMFI", "GOLD", "GOOD", "GPRA", "GSMF", "GTRA", "GTSI", "GULA", "HADI", "HAIS", "HAPS", "HATM", "HDFA", "HDIT", "HEAL", "HELI", "HERO", "HEXA", "HITS", "HKMU", "HKTI", "HMSP", "HOPE", "HRME", "HRTA", "HUMI", "HYAM", "IBST", "ICBP", "ICON", "IDEA", "IDPR", "IFII", "IGAR", "IIKP", "IKAI", "IKBI", "IKPM", "IMAS", "IMJS", "IMPC", "INAF", "INAI", "INCF", "INCI", "INCO", "INDF", "INDR", "INDX", "INDY", "INKP", "INOV", "INPC", "INPP", "INTA", "INTP", "IPCC", "IPCM", "IPOL", "ISAT", "ISSP", "ITIC", "ITMG", "JARR", "JAST", "JAYA", "JECC", "JGLE", "JIHD", "JKON", "JKSW", "JMAS", "JPFA", "JRPT", "JSKY", "KAEF", "KARW", "KAYU", "KBAG", "KBLM", "KBLV", "KBRI", "KDSI", "KICI", "KINO", "KIOS", "KKGI", "KLBF", "KMDS", "KMTR", "KOBX", "KOIN", "KONI", "KOPI", "KPAS", "KPIG", "KRAS", "KREN", "LABA", "LAPD", "LCGP", "LEAD", "LIFE", "LINK", "LION", "LMAS", "LMPI", "LMSH", "LPCK", "LPIN", "LPKR", "LPLI", "LSIP", "LTLS", "LUCY", "MAIN", "MAPA", "MAPB", "MARK", "MASA", "MAYA", "MBAP", "MBSS", "MCAS", "MCOL", "MDIA", "MDKA", "MDLN", "MEDC", "MEGA", "MERK", "META", "MFIN", "MFMI", "MGNA", "MGRO", "MICE", "MIDI", "MIKA", "MIRA", "MITI", "MKNT", "MLBI", "MLIA", "MLPL", "MLPT", "MMIX", "MMLP", "MNCN", "MNCS", "MNTO", "MPMX", "MPPA", "MRAT", "MREI", "MSIN", "MSKY", "MTDL", "MTFN", "MTLA", "MTMH", "MTPS", "MTSM", "MYOH", "MYOR", "NANO", "NASA", "NELY", "NFCX", "NICK", "NICL", "NIRO", "NISP", "NKON", "NOBU", "NRCA", "NTBK", "NUSA", "OASA", "OCAP", "OILS", "OKAS", "OMRE", "OPMS", "OPTI", "ORIN", "PACK", "PALM", "PAMG", "PANI", "PANS", "PBID", "PBRX", "PCAR", "PEGE", "PGAS", "PGEO", "PGLI", "PGUN", "PICO", "PINA", "PIPP", "PKPK", "PLAS", "PLIN", "PMJS", "PNBN", "PNBS", "PNGO", "PNIN", "PNLF", "POLA", "POLI", "POLU", "POOL", "PPGL", "PPRE", "PRAS", "PRDA", "PRIM", "PSAB", "PSDN", "PSGO", "PSKT", "PSSI", "PTBA", "PTIS", "PTPP", "PTRO", "PTSN", "PTSP", "PURE", "PWON", "RAAM", "RAJA", "RALS", "RANC", "RBMS", "RDTX", "REAL", "RELI", "RICY", "RIGS", "RISE", "RMBA", "RODA", "ROTI", "RUIS", "SAME", "SAMF", "SAPX", "SATU", "SBAT", "SBCO", "SBER", "SBMA", "SCBD", "SCMA", "SDMU", "SDPC", "SDRA", "SGER", "SGRO", "SIDO", "SILO", "SIMA", "SIMP", "SING", "SIPD", "SKBM", "SKLT", "SKRN", "SMAR", "SMBR", "SMCB", "SMDR", "SMGR", "SMIL", "SMKL", "SMKM", "SMMA", "SMMT", "SMRA", "SMSM", "SNLK", "SOCI", "SOHO", "SONA", "SPMA", "SPTO", "SRAJ", "SRTG", "SSIA", "SSMS", "SSTM", "STAR", "STTP", "SULI", "SUPR", "SURYA", "SWAT", "TALF", "TAMA", "TAMU", "TAPG", "TARA", "TAXI", "TBIG", "TBLA", "TBMS", "TCID", "TCPI", "TDPM", "TEBE", "TECH", "TELE", "TFAS", "TFCO", "TGKA", "TGRA", "TIFA", "TINS", "TKIM", "TLKM", "TMAS", "TOBA", "TOOL", "TOPS", "TOTL", "TOTO", "TOWR", "TPIA", "TPMA", "TRAM", "TRIM", "TRIN", "TRIO", "TRIS", "TRJA", "TRUK", "TSPC", "UANG", "UFOE", "ULTJ", "UNIC", "UNIQ", "UNIT", "UNSP", "UNTR", "UNVR", "VAST", "VICO", "VINS", "VIVA", "VKTR", "WAPO", "WEGE", "WICO", "WIDI", "WIIM", "WIKA", "WINE", "WINR", "WINS", "WIRG", "WIRY", "WOMF", "WOOD", "YELO", "YPAS", "YULE", "ZBRA", "ZINC"]

DEFAULT_MAX_PRICE = 1000
DEFAULT_TOP_N = 30

PRESETS = {
    "IDX Top 100": SYMBOLS[:100],
    "IDX Top 300": SYMBOLS[:300],
    "IDX Top 500": SYMBOLS[:500],
    "All Master": SYMBOLS,
    "Custom": []
}


# =========================================================
# GLOBAL STYLE
# =========================================================
st.markdown("""
<style>
.stApp {
    background: linear-gradient(180deg, #071019 0%, #0a1320 100%);
    color: #e8f0ff;
}
.block-container {
    max-width: 99%;
    padding-top: 0.8rem;
    padding-bottom: 1rem;
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
# FORMAT HELPERS
# =========================================================
def normalize_jk_symbol(symbol: str) -> str:
    s = str(symbol).strip().upper().replace(" ", "")
    if not s:
        return ""
    if ":" in s:
        return s
    if not s.endswith(".JK"):
        s = f"{s}.JK"
    return s


def clean_symbol(symbol: str) -> str:
    return str(symbol).replace(".JK", "").strip().upper()


def latest(series: pd.Series) -> float:
    try:
        return float(series.iloc[-1])
    except Exception:
        return np.nan


def fmt_price(v):
    try:
        if pd.isna(v):
            return "-"
        if abs(float(v)) >= 100:
            return f"{float(v):,.0f}"
        return f"{float(v):,.2f}"
    except Exception:
        return "-"


def fmt_pct(v):
    try:
        if pd.isna(v):
            return "-"
        return f"{float(v):.1f}%"
    except Exception:
        return "-"


def rsi_cell_text(v):
    try:
        if pd.isna(v):
            return "-"
        return f"{float(v):.1f}"
    except Exception:
        return "-"


def human_value(v):
    try:
        if pd.isna(v):
            return "-"
        v = float(v)
        if v >= 1_000_000_000_000:
            return f"{v / 1_000_000_000_000:.1f}T"
        if v >= 1_000_000_000:
            return f"{v / 1_000_000_000:.1f}B"
        if v >= 1_000_000:
            return f"{v / 1_000_000:.1f}M"
        return f"{v:,.0f}"
    except Exception:
        return "-"


# =========================================================
# WATCHLIST ENGINE — BAGIAN YANG DIPERBAIKI
# =========================================================
def parse_custom_symbols(text_value: str) -> list[str]:
    if not text_value:
        return []
    raw = re_split_symbols(text_value)
    cleaned = []
    for item in raw:
        s = clean_symbol(item)
        if s:
            cleaned.append(s)
    return list(dict.fromkeys(cleaned))


def re_split_symbols(text_value: str) -> list[str]:
    # Bisa terima format: AALI,BBCA\nGOTO BSJP;BMRI
    import re
    return [x for x in re.split(r"[\s,;|]+", str(text_value)) if x.strip()]


def build_watchlist(
    preset_name: str,
    custom_text: str,
    manual_symbol: str,
    manual_mode: str,
    scan_limit: int,
    include_price_suffix: bool = True
) -> list[str]:
    if preset_name == "Custom":
        base = parse_custom_symbols(custom_text)
    else:
        base = [clean_symbol(x) for x in PRESETS.get(preset_name, [])]

    manual = clean_symbol(manual_symbol)

    if manual:
        if manual_mode == "Analisa emiten ini saja":
            base = [manual]
        elif manual_mode == "Tambahkan ke watchlist":
            base.append(manual)
        elif manual_mode == "Hapus dari watchlist":
            base = [x for x in base if x != manual]

    base = [x for x in base if x]
    base = list(dict.fromkeys(base))

    if scan_limit and scan_limit > 0:
        base = base[:scan_limit]

    if include_price_suffix:
        return [normalize_jk_symbol(x) for x in base]
    return base


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


def signal_emoji(signal: str, trend: str = "", gain: float = 0) -> str:
    s = str(signal).upper()
    t = str(trend).upper()

    if s in ["SUPER", "ON TRACK", "HAKA", "AKUM", "GC NOW"]:
        return "🔥 BUY"
    if s == "REBOUND":
        return "🔄 REBOUND"
    if s in ["DIST", "WASPADA OB"]:
        return "⚠️ SELL/WATCH"
    if t == "BULL" and gain >= 0:
        return "📈 HOLD"
    if t == "BEAR" or gain < -3:
        return "🔻 SELL"
    return "⏳ WAIT"


def risk_level(score_accum: float, rsi: float, signal: str) -> str:
    s = str(signal).upper()
    if s in ["DIST", "WASPADA OB"] or (not pd.isna(rsi) and rsi >= 72):
        return "HIGH"
    if score_accum >= 70:
        return "LOW"
    if score_accum >= 50:
        return "MEDIUM"
    return "HIGH"


def build_box_telegram_message(row):
    symbol = row["symbol"]

    now = fmt_price(row["now"])
    gain = fmt_pct(row["gain"])
    rvol = fmt_pct(row["rvol"])
    value = human_value(row["val"])
    rsi = rsi_cell_text(row["rsi"])

    trend = str(row["trend"])
    fase = str(row["fase"])
    sinyal = str(row["sinyal"])

    support = fmt_price(row["support"])
    resistance = fmt_price(row["resistance"])
    entry_zone = str(row.get("entry_zone", fmt_price(row["entry"])))
    entry_status = str(row.get("entry_status", "-"))
    sl = fmt_price(row["sl"])
    tp_zone = str(row.get("tp_zone", fmt_price(row["tp"])))

    arah = "▼" if row["gain"] < 0 else "▲"
    risk = risk_level(row["score_accum"], row["rsi"], row["sinyal"])
    sig = signal_emoji(row["sinyal"], row["trend"], row["gain"])

    message = f"""<pre>
┌──────────────────────────────────────────────┐
│ {symbol:<6} | AI STOCK SCREENER              │
│ Harga : {now:<7} {arah} {gain:<9}            │
│ RVOL  : {rvol:<7} | Value : {value:<10}      │
├──────────────────────────────────────────────┤
│ Trend      : {trend[:28]:<28}│
│ Fase       : {fase[:28]:<28}│
│ Support    : {support:<28}│
│ Resistance : {resistance:<28}│
│ RSI        : {rsi:<28}│
├──────────────────────────────────────────────┤
│ AI Score   : {int(row["score_accum"]):<28}│
│ Bandar     : {int(row["score_bandar"]):<28}│
│ Momentum   : {int(row["score_total"]):<28}│
│ Risiko     : {risk:<28}│
├──────────────────────────────────────────────┤
│ Sinyal     : {sig[:28]:<28}│
│ Detail     : {sinyal[:28]:<28}│
│ Entry Zone : {entry_zone:<28}│
│ Status     : {entry_status:<28}│
│ Stop Loss  : {sl:<28}│
│ TP1/2/3    : {tp_zone:<28}│
└──────────────────────────────────────────────┘
</pre>"""
    return message


def send_rows_to_telegram(bot_token: str, chat_id: str, df: pd.DataFrame, max_rows: int):
    if df.empty:
        return 0, "Tidak ada data untuk dikirim"

    success_count = 0
    failed_msg = ""

    # Kirim 1 saham = 1 pesan agar tidak kena limit 4096 karakter Telegram
    for _, row in df.head(max_rows).iterrows():
        message = build_box_telegram_message(row)
        ok, msg = send_telegram_message(bot_token, chat_id, message)
        if ok:
            success_count += 1
            time.sleep(0.25)
        else:
            failed_msg = msg

    if success_count > 0:
        return success_count, "Terkirim"
    return 0, failed_msg or "Gagal kirim Telegram"


# =========================================================
# DATA SOURCE
# =========================================================
@st.cache_data(ttl=300, show_spinner=False)
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

        df = df.dropna(subset=["Open", "High", "Low", "Close"]).copy()
        df["Volume"] = df["Volume"].fillna(0)
        return df
    except Exception:
        return pd.DataFrame()


@st.cache_data(ttl=300, show_spinner=False)
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

    candle_range = (x["High"] - x["Low"]).replace(0, np.nan)
    upper_wick = x["High"] - x[["Open", "Close"]].max(axis=1)
    lower_wick = x[["Open", "Close"]].min(axis=1) - x["Low"]
    x["WICK_PCT"] = ((upper_wick.clip(lower=0) + lower_wick.clip(lower=0)) / candle_range) * 100

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
    if signal_label == "SUPER":
        return "SIAP BELI"
    if signal_label in ["ON TRACK", "AKUM", "HAKA", "GC NOW", "REBOUND"]:
        if not pd.isna(entry) and close_ <= entry * 1.02:
            return "AT ENTRY"
        return "WATCH"
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
        elif rsi >= 72:
            score -= 8

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
    elif signal in ["DIST", "WASPADA OB"]:
        score -= 8

    if not pd.isna(gain):
        if gain > 0:
            score += 4
        elif gain < -3:
            score -= 5

    return max(score, 0)



# =========================================================
# ENTRY ZONE ENGINE
# =========================================================
def build_entry_zone(close_, support, ma20, atr, resistance):
    """Membuat zona entry otomatis berbasis support, MA20, dan ATR."""
    if pd.isna(close_):
        return {
            "entry_low": np.nan,
            "entry_high": np.nan,
            "entry_zone": "-",
            "entry_status": "WAIT DATA",
        }

    if pd.isna(atr) or atr <= 0:
        atr = close_ * 0.03

    if not pd.isna(support) and not pd.isna(ma20):
        base = (support + ma20) / 2
    elif not pd.isna(support):
        base = support
    elif not pd.isna(ma20):
        base = ma20
    else:
        base = close_

    entry_low = round(base - (atr * 0.30))
    entry_high = round(base + (atr * 0.30))

    if close_ < entry_low:
        entry_status = "BELOW ZONE"
    elif entry_low <= close_ <= entry_high:
        entry_status = "IN ZONE"
    elif not pd.isna(resistance) and close_ >= resistance * 0.985:
        entry_status = "BREAKOUT ZONE"
    else:
        entry_status = "ABOVE ZONE"

    return {
        "entry_low": entry_low,
        "entry_high": entry_high,
        "entry_zone": f"{fmt_price(entry_low)} - {fmt_price(entry_high)}",
        "entry_status": entry_status,
    }


def bg_entry_status(v):
    return {
        "IN ZONE": "#16a34a",
        "BREAKOUT ZONE": "#9333ea",
        "ABOVE ZONE": "#d97706",
        "BELOW ZONE": "#2563eb",
        "WAIT DATA": "#374151",
    }.get(str(v), "#374151")

# =========================================================
# ROW BUILDER
# =========================================================
def build_row(symbol: str, daily_df: pd.DataFrame, intraday_5m: pd.DataFrame):
    df = calc_indicators(daily_df)
    if len(df) < 55:
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

    zone = build_entry_zone(
        close_=close_,
        support=support,
        ma20=ma20,
        atr=atr,
        resistance=resistance,
    )

    entry_low = zone["entry_low"]
    entry_high = zone["entry_high"]
    entry_zone = zone["entry_zone"]
    entry_status = zone["entry_status"]
    entry = entry_low

    if pd.isna(atr) or atr <= 0:
        atr = close_ * 0.03 if not pd.isna(close_) else 0

    tp1 = round(close_ + (atr * 1.0)) if not pd.isna(close_) else np.nan
    tp2 = round(close_ + (atr * 2.0)) if not pd.isna(close_) else np.nan
    tp3 = round(close_ + (atr * 3.0)) if not pd.isna(close_) else np.nan
    tp = tp2
    tp_zone = f"{fmt_price(tp1)} / {fmt_price(tp2)} / {fmt_price(tp3)}"

    sl = round(entry_low - (atr * 0.70)) if not pd.isna(entry_low) else np.nan
    profit = ((close_ - entry) / entry * 100) if entry and not pd.isna(entry) else 0.0
    to_tp = ((tp - close_) / close_ * 100) if close_ and not pd.isna(tp) else 0.0

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
        "symbol": clean_symbol(symbol),
        "full_symbol": symbol,
        "gain": gain,
        "wick": wick,
        "aksi": aksi,
        "sinyal": sinyal,
        "emoji_signal": signal_emoji(sinyal, trend, gain),
        "rvol": rvol,
        "entry": entry,
        "entry_low": entry_low,
        "entry_high": entry_high,
        "entry_zone": entry_zone,
        "entry_status": entry_status,
        "now": close_,
        "tp": tp,
        "tp1": tp1,
        "tp2": tp2,
        "tp3": tp3,
        "tp_zone": tp_zone,
        "sl": sl,
        "support": support,
        "resistance": resistance,
        "profit": profit,
        "to_tp": to_tp,
        "rsi": rsi,
        "rsi_sig": rsi_sig,
        "rsi_5m": intraday_rsi,
        "val": val,
        "fase": phase,
        "trend": trend,
        "risk": risk_level(accum_score, rsi, sinyal),
        "score_scalping": scores["scalping"],
        "score_bsjp": scores["bsjp"],
        "score_swing": scores["swing"],
        "score_bandar": scores["bandar"],
        "score_total": total,
        "score_accum": accum_score,
        "daily_df": df,
    }


@st.cache_data(ttl=300, show_spinner=False)
def run_screener_cached(symbols_tuple, period, interval, max_price, min_price, use_intraday):
    rows = []
    failed = 0

    for symbol in symbols_tuple:
        try:
            daily = get_ohlcv(symbol, period=period, interval=interval)
            if daily.empty:
                failed += 1
                continue

            intra5 = get_intraday_5m(symbol) if use_intraday else pd.DataFrame()
            row = build_row(symbol, daily, intra5)

            if row is None:
                failed += 1
                continue

            if pd.isna(row["now"]):
                failed += 1
                continue

            if row["now"] < min_price or row["now"] > max_price:
                continue

            rows.append(row)

        except Exception:
            failed += 1
            continue

    if not rows:
        return pd.DataFrame(), failed

    df = pd.DataFrame(rows)
    df = df.sort_values(
        ["score_accum", "score_total", "rvol", "gain"],
        ascending=[False, False, False, False]
    ).reset_index(drop=True)

    return df, failed


# =========================================================
# FILTER ENGINE — BAGIAN YANG DIPERBAIKI
# =========================================================
def apply_filters(
    df: pd.DataFrame,
    min_score: int,
    min_total_score: int,
    min_rvol: int,
    min_value: float,
    selected_signals: list[str],
    selected_trends: list[str],
    selected_phases: list[str],
    only_top_signal: bool,
):
    if df.empty:
        return df

    x = df.copy()

    x = x[x["score_accum"] >= min_score]
    x = x[x["score_total"] >= min_total_score]

    if min_rvol > 0:
        x = x[x["rvol"].fillna(0) >= min_rvol]

    if min_value > 0:
        x = x[x["val"].fillna(0) >= min_value]

    if selected_signals:
        x = x[x["sinyal"].isin(selected_signals)]

    if selected_trends:
        x = x[x["trend"].isin(selected_trends)]

    if selected_phases:
        x = x[x["fase"].isin(selected_phases)]

    if only_top_signal:
        x = x[
            (x["sinyal"].isin(["SUPER", "ON TRACK", "AKUM", "HAKA", "GC NOW"])) |
            ((x["score_accum"] >= 60) & (x["rvol"].fillna(0) >= 120))
        ]

    return x.sort_values(
        ["score_accum", "score_total", "rvol", "gain"],
        ascending=[False, False, False, False]
    ).reset_index(drop=True)


# =========================================================
# HTML TABLE
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


def bg_signal(v):
    mapping = {
        "SUPER": "#7e22ce",
        "ON TRACK": "#16a34a",
        "AKUM": "#15803d",
        "HAKA": "#14b8a6",
        "GC NOW": "#9333ea",
        "REBOUND": "#d97706",
        "WASPADA OB": "#ea580c",
        "DIST": "#b91c1c",
        "WAIT": "#111827",
    }
    return mapping.get(str(v), "#334155")


def bg_score(v):
    if pd.isna(v):
        return "#243244"
    if v >= 70:
        return "#9333ea"
    if v >= 55:
        return "#16a34a"
    if v >= 40:
        return "#2563eb"
    return "#374151"


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


def bg_trend(v):
    return {"BULL": "#16a34a", "BEAR": "#dc2626", "NEUTRAL": "#6b7280"}.get(str(v), "#334155")


def bg_phase(v):
    return {"BIG AKUM": "#9333ea", "AKUM": "#16a34a", "NEUTRAL": "#374151", "DIST": "#dc2626", "BIG DIST": "#991b1b"}.get(str(v), "#334155")


def bg_risk(v):
    return {"LOW": "#16a34a", "MEDIUM": "#d97706", "HIGH": "#b91c1c"}.get(str(v), "#334155")


def make_html_table(df: pd.DataFrame, title: str, sub: str):
    html = """
    <html>
    <head>
    <style>
    body {
        margin: 0;
        background: #07111b;
        color: white;
        font-family: Arial, Helvetica, sans-serif;
    }
    .screen-box {
        border: 1px solid #17324d;
        border-radius: 10px;
        padding: 8px;
        background: #07111b;
        box-sizing: border-box;
        width: 100%;
    }
    .screener-title {
        text-align: center;
        font-weight: 900;
        font-size: 15px;
        color: #eaf2ff;
        margin-bottom: 4px;
        letter-spacing: 0.3px;
    }
    .screener-sub {
        text-align: center;
        color: #9fb5d1;
        font-size: 11px;
        margin-bottom: 8px;
    }
    .table-wrap {
        width: 100%;
        overflow-x: auto;
    }
    .custom-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 11px;
        min-width: 1850px;
    }
    .custom-table th {
        background: #184574;
        color: #ffffff;
        border: 1px solid #2a527b;
        padding: 6px 4px;
        text-align: center;
        white-space: nowrap;
        font-weight: 900;
    }
    .custom-table td {
        border: 1px solid #20364e;
        padding: 5px 4px;
        text-align: center;
        white-space: nowrap;
        font-weight: 800;
    }
    .footer-line {
        margin-top: 6px;
        text-align: center;
        color: #ffd451;
        font-size: 10px;
        font-weight: 700;
    }
    </style>
    </head>
    <body>
    <div class="screen-box">
    """
    html += f"""
      <div class="screener-title">{title}</div>
      <div class="screener-sub">{sub}</div>
      <div class="table-wrap">
      <table class="custom-table">
        <thead>
          <tr>
            <th>RANK</th>
            <th>EMITEN</th>
            <th>SIGNAL</th>
            <th>AI SCORE</th>
            <th>TOTAL</th>
            <th>GAIN</th>
            <th>RVOL</th>
            <th>NOW</th>
            <th>ENTRY ZONE</th>
            <th>ENTRY STATUS</th>
            <th>TP1/TP2/TP3</th>
            <th>SL</th>
            <th>RSI</th>
            <th>RSI 5M</th>
            <th>VALUE</th>
            <th>FASE</th>
            <th>TREND</th>
            <th>RISK</th>
            <th>AKSI</th>
            <th>DETAIL</th>
          </tr>
        </thead>
        <tbody>
    """

    for i, (_, row) in enumerate(df.iterrows(), start=1):
        html += f"""
        <tr>
            <td style="background:#0f172a;color:#fff;">{i}</td>
            <td style="background:#1d4ed8;color:#fff;">{row['symbol']}</td>
            <td style="background:{bg_signal(row['sinyal'])};color:#fff;">{row['emoji_signal']}</td>
            <td style="background:{bg_score(row['score_accum'])};color:#fff;">{int(row['score_accum'])}</td>
            <td style="background:#0b3b66;color:#fff;">{int(row['score_total'])}</td>
            <td style="background:{bg_gain(row['gain'])};color:#fff;">{fmt_pct(row['gain'])}</td>
            <td style="background:{bg_rvol(row['rvol'])};color:#fff;">{fmt_pct(row['rvol'])}</td>
            <td style="background:#2563eb;color:#fff;">{fmt_price(row['now'])}</td>
            <td style="background:#1d4ed8;color:#fff;">{row.get('entry_zone', fmt_price(row['entry']))}</td>
            <td style="background:{bg_entry_status(row.get('entry_status', '-'))};color:#fff;">{row.get('entry_status', '-')}</td>
            <td style="background:#16a34a;color:#fff;">{row.get('tp_zone', fmt_price(row['tp']))}</td>
            <td style="background:#b91c1c;color:#fff;">{fmt_price(row['sl'])}</td>
            <td style="background:#374151;color:#fff;">{rsi_cell_text(row['rsi'])}</td>
            <td style="background:#374151;color:#fff;">{rsi_cell_text(row['rsi_5m'])}</td>
            <td style="background:#183b69;color:#fff;">{human_value(row['val'])}</td>
            <td style="background:{bg_phase(row['fase'])};color:#fff;">{row['fase']}</td>
            <td style="background:{bg_trend(row['trend'])};color:#fff;">{row['trend']}</td>
            <td style="background:{bg_risk(row['risk'])};color:#fff;">{row['risk']}</td>
            <td style="background:#334155;color:#fff;">{row['aksi']}</td>
            <td style="background:{bg_signal(row['sinyal'])};color:#fff;">{row['sinyal']}</td>
        </tr>
        """

    html += """
        </tbody>
      </table>
      </div>
      <div class="footer-line">Final fixed watchlist + entry zone | filter aktif | Telegram per saham | anti message-too-long | anti-spam refresh</div>
    </div>
    </body>
    </html>
    """
    return html



# =========================================================
# HEADER
# =========================================================
st.title("IDX AI SCREENER — FINAL FIXED WATCHLIST")
st.markdown(
    '<div class="small-note">All Master / IDX Top / Custom sudah diperbaiki | Filter lengkap | Top Signal Telegram | Auto Refresh Anti-Spam</div>',
    unsafe_allow_html=True
)


# =========================================================
# SIDEBAR
# =========================================================
with st.sidebar:
    st.header("1. Watchlist")

    preset_name = st.selectbox("Preset Watchlist", list(PRESETS.keys()), index=0)

    default_custom = ""
    if preset_name != "Custom":
        default_custom = ",".join(PRESETS[preset_name][:50])

    custom_symbols = st.text_area(
        "Custom watchlist / preview preset",
        value=default_custom if preset_name == "Custom" else ",".join(PRESETS[preset_name][:100]),
        height=150,
        help="Bisa isi: BBCA, BBRI, GOTO atau per baris."
    )

    manual_symbol = st.text_input("Cari / tambah / hapus emiten", placeholder="Contoh: BSJP")
    manual_mode = st.radio(
        "Mode manual",
        ["Tambahkan ke watchlist", "Analisa emiten ini saja", "Hapus dari watchlist"],
        index=0
    )

    scan_limit = st.number_input(
        "Batas jumlah emiten discan",
        min_value=1,
        max_value=len(SYMBOLS),
        value=100,
        step=50,
        help="Untuk All Master, naikkan pelan-pelan. 581 saham bisa lambat jika pakai yfinance."
    )

    st.markdown("---")
    st.header("2. Data & Filter")

    period = st.selectbox("Periode data", ["3mo", "6mo", "1y", "2y"], index=1)
    interval = st.selectbox("Interval", ["1d", "1wk"], index=0)
    use_intraday = st.checkbox("Ambil RSI 5M", value=False, help="Lebih berat. Matikan jika scan All Master.")

    min_price = st.number_input("Harga minimum", min_value=0, value=0, step=10)
    max_price = st.number_input("Harga maksimum", min_value=1, value=DEFAULT_MAX_PRICE, step=50)

    min_score = st.slider("Minimal AI Score", 0, 100, 40)
    min_total_score = st.slider("Minimal Total Score", 0, 30, 0)
    min_rvol = st.slider("Minimal RVOL %", 0, 500, 0)
    min_value_b = st.number_input("Minimal Value (Biliar)", min_value=0.0, value=0.0, step=1.0)
    min_value = min_value_b * 1_000_000_000

    signal_options = ["SUPER", "ON TRACK", "AKUM", "HAKA", "GC NOW", "REBOUND", "WAIT", "WASPADA OB", "DIST"]
    selected_signals = st.multiselect("Filter Sinyal", signal_options, default=[])

    selected_trends = st.multiselect("Filter Trend", ["BULL", "BEAR", "NEUTRAL"], default=[])
    selected_phases = st.multiselect("Filter Fase", ["BIG AKUM", "AKUM", "NEUTRAL", "DIST", "BIG DIST"], default=[])

    only_top_signal = st.checkbox("Tampilkan hanya TOP SIGNAL", value=False)
    top_n_display = st.number_input("Jumlah hasil tabel", min_value=5, max_value=100, value=DEFAULT_TOP_N, step=5)

    st.markdown("---")
    st.header("3. Telegram")

    telegram_enabled = st.checkbox("Aktifkan Telegram", value=False)
    telegram_bot_token = st.text_input("Bot Token", type="password")
    telegram_chat_id = st.text_input("Chat ID")
    telegram_top_n = st.number_input("Kirim Top N", min_value=1, max_value=10, value=5, step=1)
    telegram_only_top_signal = st.checkbox("Telegram hanya TOP SIGNAL", value=True)

    send_test_btn = st.button("Tes Kirim Telegram", use_container_width=True)

    st.markdown("---")
    st.header("4. Auto")

    auto_refresh = st.checkbox("Auto Refresh", value=False)
    refresh_sec = st.selectbox("Refresh tiap", [30, 60, 120, 300, 600], index=2)
    auto_send_telegram = st.checkbox("Auto kirim Telegram tiap refresh", value=False)

    run_btn = st.button("🚀 Jalankan Screener", use_container_width=True)


# =========================================================
# TELEGRAM TEST
# =========================================================
if send_test_btn:
    now_text = datetime.now(WIB).strftime("%d-%m-%Y %H:%M:%S WIB")
    test_message = (
        "🤖 <b>Test Notifikasi Berhasil</b>\n"
        "✅ Bot Telegram sudah terhubung.\n\n"
        f"🕒 <b>Waktu:</b> {now_text}\n"
        "📡 <b>Status:</b> ONLINE"
    )
    ok, msg = send_telegram_message(telegram_bot_token, telegram_chat_id, test_message)
    if ok:
        st.success("Pesan test berhasil dikirim.")
    else:
        st.error(f"Gagal kirim test: {msg}")


# =========================================================
# BUILD WATCHLIST
# =========================================================
symbols = build_watchlist(
    preset_name=preset_name,
    custom_text=custom_symbols,
    manual_symbol=manual_symbol,
    manual_mode=manual_mode,
    scan_limit=int(scan_limit),
    include_price_suffix=True
)

if not symbols:
    st.warning("Watchlist kosong. Pilih preset atau isi custom symbol.")
    st.stop()

with st.expander("Preview watchlist yang akan discan", expanded=False):
    st.write(f"Jumlah emiten: **{len(symbols)}**")
    st.code(", ".join([clean_symbol(x) for x in symbols[:300]]) + (" ..." if len(symbols) > 300 else ""))


# =========================================================
# RUN SCREENER
# =========================================================
should_run = run_btn or "raw_screener_df" not in st.session_state

if should_run:
    with st.spinner(f"Mengambil data {len(symbols)} emiten..."):
        raw_df, failed_count = run_screener_cached(
            tuple(symbols),
            period,
            interval,
            float(max_price),
            float(min_price),
            bool(use_intraday)
        )
        st.session_state["raw_screener_df"] = raw_df
        st.session_state["failed_count"] = failed_count
        st.session_state["last_run"] = datetime.now(WIB).strftime("%Y-%m-%d %H:%M:%S WIB")

raw_df = st.session_state.get("raw_screener_df", pd.DataFrame())
failed_count = st.session_state.get("failed_count", 0)
last_run = st.session_state.get("last_run", "-")

if raw_df.empty:
    st.error("Tidak ada data yang berhasil discan / lolos harga. Coba naikkan batas harga, turunkan scan limit, atau ganti preset.")
    st.stop()

filtered_df = apply_filters(
    raw_df,
    min_score=int(min_score),
    min_total_score=int(min_total_score),
    min_rvol=int(min_rvol),
    min_value=float(min_value),
    selected_signals=selected_signals,
    selected_trends=selected_trends,
    selected_phases=selected_phases,
    only_top_signal=bool(only_top_signal),
)

display_df = filtered_df.head(int(top_n_display)).reset_index(drop=True)

if telegram_only_top_signal:
    telegram_df = apply_filters(
        raw_df,
        min_score=max(int(min_score), 50),
        min_total_score=int(min_total_score),
        min_rvol=max(int(min_rvol), 100),
        min_value=float(min_value),
        selected_signals=["SUPER", "ON TRACK", "AKUM", "HAKA", "GC NOW"],
        selected_trends=selected_trends,
        selected_phases=selected_phases,
        only_top_signal=True,
    )
else:
    telegram_df = display_df.copy()


# =========================================================
# AUTO TELEGRAM ANTI-SPAM
# =========================================================
if telegram_enabled and auto_refresh and auto_send_telegram and telegram_bot_token and telegram_chat_id and not telegram_df.empty:
    send_source = telegram_df.head(int(telegram_top_n))
    current_alert_key = "|".join([
        f"{row['symbol']}-{int(row['score_accum'])}-{row['sinyal']}-{fmt_price(row['now'])}"
        for _, row in send_source.iterrows()
    ])
    last_alert_key = st.session_state.get("last_alert_key", "")

    if current_alert_key != last_alert_key:
        success_count, msg = send_rows_to_telegram(
            telegram_bot_token,
            telegram_chat_id,
            send_source,
            int(telegram_top_n)
        )
        if success_count > 0:
            st.session_state["last_alert_key"] = current_alert_key
            st.success(f"✅ Auto Telegram terkirim: {success_count} saham")
        else:
            st.warning(f"❌ Gagal auto Telegram: {msg}")


# =========================================================
# TOP METRICS
# =========================================================
top_symbol = display_df.iloc[0]["symbol"] if not display_df.empty else "-"
top_score = int(display_df.iloc[0]["score_accum"]) if not display_df.empty else 0
top_signal = display_df.iloc[0]["emoji_signal"] if not display_df.empty else "-"

m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("RAW SCANNED", len(raw_df))
m2.metric("FILTERED", len(filtered_df))
m3.metric("TOP PICK", top_symbol)
m4.metric("AI SCORE", top_score)
m5.metric("LAST SCAN", last_run)

m6, m7, m8 = st.columns(3)
m6.metric("TOP SIGNAL", top_signal)
m7.metric("FAILED / EMPTY", failed_count)
m8.metric("WATCHLIST SIZE", len(symbols))


# =========================================================
# TELEGRAM MANUAL BUTTON
# =========================================================
send_now_btn = st.button("📨 Kirim TOP SIGNAL ke Telegram", use_container_width=True)

if telegram_enabled and send_now_btn:
    target_df = telegram_df.head(int(telegram_top_n))

    if target_df.empty:
        st.warning("Tidak ada TOP SIGNAL untuk dikirim.")
    else:
        success_count, msg = send_rows_to_telegram(
            telegram_bot_token,
            telegram_chat_id,
            target_df,
            int(telegram_top_n)
        )

        if success_count > 0:
            st.success(f"✅ {success_count} alert berhasil dikirim ke Telegram.")
        else:
            st.error(f"❌ Gagal kirim Telegram: {msg}")


# =========================================================
# MAIN TABLE
# =========================================================
st.subheader("📊 Hasil Screener")

if display_df.empty:
    st.warning("Tidak ada saham yang lolos filter. Turunkan minimal AI Score / RVOL / Value.")
else:
    components.html(
        make_html_table(
            display_df,
            "IDX AI SCREENER — FINAL FIXED WATCHLIST",
            "Ranking berdasarkan AI Score + Total Score + RVOL + Gain"
        ),
        height=560,
        scrolling=True
    )

    st.subheader("Ranking Data")
    rank_df = display_df[[
        "symbol", "emoji_signal", "now", "entry_zone", "entry_status", "tp_zone", "sl",
        "gain", "rvol", "rsi", "rsi_5m", "val", "fase", "trend", "risk", "sinyal",
        "score_accum", "score_scalping", "score_bsjp", "score_swing", "score_bandar", "score_total"
    ]].copy()

    rank_df.columns = [
        "EMITEN", "SIGNAL", "PRICE", "ENTRY ZONE", "ENTRY STATUS", "TP1/TP2/TP3", "SL",
        "GAIN", "RVOL", "RSI", "RSI 5M", "VALUE", "FASE", "TREND", "RISK", "DETAIL",
        "AI SCORE", "SCALPING", "BSJP", "SWING", "BANDAR", "TOTAL"
    ]

    rank_df["PRICE"] = rank_df["PRICE"].apply(fmt_price)
    rank_df["SL"] = rank_df["SL"].apply(fmt_price)
    rank_df["GAIN"] = rank_df["GAIN"].apply(fmt_pct)
    rank_df["RVOL"] = rank_df["RVOL"].apply(fmt_pct)
    rank_df["RSI"] = rank_df["RSI"].apply(rsi_cell_text)
    rank_df["RSI 5M"] = rank_df["RSI 5M"].apply(rsi_cell_text)
    rank_df["VALUE"] = rank_df["VALUE"].apply(human_value)

    st.dataframe(rank_df, use_container_width=True, height=520)


# =========================================================
# DETAIL PANEL
# =========================================================
if not display_df.empty:
    st.subheader("🔍 Detail Emiten")
    selected_symbol = st.selectbox("Pilih saham untuk detail", display_df["full_symbol"].tolist())
    selected_row = display_df[display_df["full_symbol"] == selected_symbol].iloc[0]

    d1, d2, d3, d4, d5, d6 = st.columns(6)
    d1.metric("EMITEN", selected_row["symbol"])
    d2.metric("PRICE", fmt_price(selected_row["now"]))
    d3.metric("GAIN", fmt_pct(selected_row["gain"]))
    d4.metric("RVOL", fmt_pct(selected_row["rvol"]))
    d5.metric("AI SCORE", int(selected_row["score_accum"]))
    d6.metric("SIGNAL", selected_row["emoji_signal"])

    st.info(
        f"Entry Zone: {selected_row['entry_zone']} | "
        f"Status: {selected_row['entry_status']} | "
        f"TP1/2/3: {selected_row['tp_zone']} | "
        f"SL: {fmt_price(selected_row['sl'])} | "
        f"Support: {fmt_price(selected_row['support'])} | "
        f"Resistance: {fmt_price(selected_row['resistance'])}"
    )


# =========================================================
# AUTO REFRESH
# =========================================================
if auto_refresh:
    auto_refresh_fragment(int(refresh_sec))
