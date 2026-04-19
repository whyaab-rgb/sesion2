import time
import textwrap
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
import numpy as np
import pandas as pd
import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import streamlit.components.v1 as components
from bs4 import BeautifulSoup

st.set_page_config(page_title="High Prob Screener IDX Pro", layout="wide")

# =========================================================
# STYLE
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


def safe_ratio(a, b, default=np.nan):
    if pd.isna(a) or pd.isna(b) or b == 0:
        return default
    return a / b


# =========================================================
# IDX UNIVERSE
# =========================================================
@st.cache_data(ttl=86400)
def get_all_idx_symbols():
    urls = [
        "https://www.idx.co.id/en/market-data/stocks-data/stock-list",
        "https://www.idx.co.id/id/data-pasar/data-saham/daftar-saham/"
    ]

    headers = {"User-Agent": "Mozilla/5.0"}
    symbols = set()

    for url in urls:
        try:
            response = requests.get(url, headers=headers, timeout=20)
            response.raise_for_status()
            html = response.text

            try:
                tables = pd.read_html(html)
                for table in tables:
                    for col in table.columns:
                        name = str(col).lower()
                        if "code" in name or "kode" in name:
                            vals = table[col].astype(str).str.strip().str.upper().tolist()
                            for v in vals:
                                if 1 <= len(v) <= 5 and v.isalnum():
                                    symbols.add(f"{v}.JK")
            except Exception:
                pass

            if not symbols:
                soup = BeautifulSoup(html, "lxml")
                tokens = soup.get_text(" ", strip=True).upper().split()
                banned = {"CODE", "KODE", "IDX", "BEI", "IPO", "LIST", "STOCK", "SAHAM", "BOARD", "DATE"}
                for token in tokens:
                    token = token.strip(",.;:()[]{}")
                    if 1 <= len(token) <= 5 and token.isalnum() and token not in banned:
                        symbols.add(f"{token}.JK")

            if symbols:
                break
        except Exception:
            continue

    clean = []
    for s in sorted(symbols):
        base = s.replace(".JK", "")
        if base.isalnum() and 1 <= len(base) <= 5:
            clean.append(s)

    return clean


# =========================================================
# DATA SOURCE
# =========================================================
@st.cache_data(ttl=300)
def get_ohlcv(symbol: str, period: str = "6mo", interval: str = "1d") -> pd.DataFrame:
    df = yf.download(
        symbol,
        period=period,
        interval=interval,
        auto_adjust=False,
        progress=False,
        threads=False,
    )

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    if df.empty:
        return pd.DataFrame()

    required = ["Open", "High", "Low", "Close", "Volume"]
    for col in required:
        if col not in df.columns:
            return pd.DataFrame()

    return df.dropna(subset=["Open", "High", "Low", "Close"]).copy()


@st.cache_data(ttl=300)
def get_intraday_5m(symbol: str) -> pd.DataFrame:
    try:
        df = yf.download(
            symbol,
            period="5d",
            interval="5m",
            auto_adjust=False,
            progress=False,
            threads=False,
        )
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
    avg_loss = loss.rolling(14).mean()
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

    x["RET"] = x["Close"].pct_change() * 100

    body = (x["Close"] - x["Open"]).abs()
    upper_wick = x["High"] - x[["Open", "Close"]].max(axis=1)
    lower_wick = x[["Open", "Close"]].min(axis=1) - x["Low"]
    candle_range = (x["High"] - x["Low"]).replace(0, np.nan)

    x["BODY"] = body
    x["UPPER_WICK"] = upper_wick.clip(lower=0)
    x["LOWER_WICK"] = lower_wick.clip(lower=0)
    x["WICK_PCT"] = ((x["UPPER_WICK"] + x["LOWER_WICK"]) / candle_range) * 100

    x["VALUE"] = x["Close"] * x["Volume"]
    x["AVG_VALUE20"] = x["VALUE"].rolling(20).mean()

    return x


# =========================================================
# LOGIC
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
    atr = latest(df["ATR14"])
    avg_value20 = latest(df["AVG_VALUE20"])

    risk_reward_bonus = 0
    if not pd.isna(atr) and atr > 0 and not pd.isna(close_):
        tp = close_ + 2 * atr
        sl = close_ - atr
        rr = safe_ratio(tp - close_, close_ - sl, default=0)
        if rr >= 1.8:
            risk_reward_bonus = 1

    liquidity_bonus = 0
    if not pd.isna(avg_value20):
        if avg_value20 >= 10_000_000_000:
            liquidity_bonus = 2
        elif avg_value20 >= 3_000_000_000:
            liquidity_bonus = 1

    scalping = 0
    if close_ > ema9 > ma20:
        scalping += 3
    if 55 <= rsi <= 72:
        scalping += 2
    if macd > macd_signal:
        scalping += 2
    if volume > vol_ma5:
        scalping += 2
    if close_ >= resistance * 0.985:
        scalping += 1
    if wick < 35:
        scalping += 1
    scalping += risk_reward_bonus
    scalping += liquidity_bonus

    bsjp = 0
    if rsi < 35:
        bsjp += 3
    elif 35 <= rsi <= 45:
        bsjp += 1
    if close_ <= bb_lower * 1.03:
        bsjp += 2
    if close_ <= support * 1.05:
        bsjp += 2
    if len(df) > 1 and df["Close"].iloc[-1] > df["Close"].iloc[-2]:
        bsjp += 1
    if df["MACD_HIST"].iloc[-1] > 0:
        bsjp += 2
    bsjp += liquidity_bonus

    swing = 0
    if close_ > ma20 > ma50:
        swing += 3
    if 50 <= rsi <= 65:
        swing += 2
    if macd > macd_signal:
        swing += 2
    if volume > vol_ma20:
        swing += 1
    if close_ < resistance * 0.93 and close_ > support * 1.08:
        swing += 1
    swing += risk_reward_bonus
    swing += liquidity_bonus

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
    if volume > vol_ma20 * 1.2:
        bandar += 2
    if close_ > ma20:
        bandar += 1
    bandar += liquidity_bonus

    return {
        "scalping": scalping,
        "bsjp": bsjp,
        "swing": swing,
        "bandar": bandar
    }


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

    rvol = safe_ratio(vol, vol_ma20, default=np.nan)
    if not pd.isna(rvol):
        rvol = rvol * 100

    entry = round((support + ma20) / 2) if not pd.isna(support) and not pd.isna(ma20) else close_
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
        "daily_df": df
    }


# =========================================================
# FILTER + SCAN
# =========================================================
def passes_prefilter(daily_df: pd.DataFrame, min_price=50, min_avg_vol=100_000, min_value=1_000_000_000):
    if daily_df.empty or len(daily_df) < 25:
        return False

    close_ = latest(daily_df["Close"])
    avg_vol20 = daily_df["Volume"].tail(20).mean()
    avg_value20 = (daily_df["Close"] * daily_df["Volume"]).tail(20).mean()

    if pd.isna(close_) or pd.isna(avg_vol20) or pd.isna(avg_value20):
        return False

    return (
        close_ >= min_price
        and avg_vol20 >= min_avg_vol
        and avg_value20 >= min_value
    )


def sort_by_strategy(df: pd.DataFrame, strategy_mode: str) -> pd.DataFrame:
    if df.empty:
        return df

    if strategy_mode == "Scalping":
        return df.sort_values(["score_scalping", "score_total", "rvol"], ascending=False).reset_index(drop=True)
    if strategy_mode == "BSJP":
        return df.sort_values(["score_bsjp", "score_total", "rsi_5m"], ascending=[False, False, True]).reset_index(drop=True)
    if strategy_mode == "Swing":
        return df.sort_values(["score_swing", "score_bandar", "score_total"], ascending=False).reset_index(drop=True)

    return df.sort_values(["score_total", "score_scalping", "score_swing"], ascending=False).reset_index(drop=True)


def run_screener_pro(symbols, period, interval, min_price, min_avg_vol, min_value, limit_scan=200, max_workers=10):
    rows = []
    scanned = 0
    passed_prefilter = 0

    progress = st.progress(0)
    status = st.empty()

    symbols = symbols[:limit_scan]

    def process_symbol(symbol):
        try:
            daily = get_ohlcv(symbol, period=period, interval=interval)
            if daily.empty:
                return None, False

            if not passes_prefilter(daily, min_price, min_avg_vol, min_value):
                return None, False

            intra = get_intraday_5m(symbol)
            row = build_row(symbol, daily, intra)
            return row, True
        except Exception:
            return None, False

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(process_symbol, symbol) for symbol in symbols]

        total_jobs = len(futures)
        for i, future in enumerate(as_completed(futures), start=1):
            row, passed = future.result()
            scanned += 1
            if passed:
                passed_prefilter += 1
            if row is not None:
                rows.append(row)

            progress.progress(i / total_jobs)
            status.text(f"Scanning {i}/{total_jobs} emiten...")

    progress.empty()
    status.empty()

    result = pd.DataFrame(rows)
    if not result.empty:
        result = result.sort_values("score_total", ascending=False).reset_index(drop=True)

    return result, scanned, passed_prefilter


# =========================================================
# COLORS
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
    if v < 1:
        return "#0f766e"
    if v < 2.5:
        return "#2563eb"
    if v < 4:
        return "#d97706"
    return "#dc2626"


def bg_aksi(v):
    return {
        "AT ENTRY": "#1d4ed8",
        "WATCH": "#b45309",
        "WAIT GC": "#374151",
        "HOLD": "#2563eb",
        "SIAP BELI": "#7c3aed",
        "WASPADA OB": "#d97706"
    }.get(v, "#334155")


def bg_sinyal(v):
    return {
        "ON TRACK": "#16a34a",
        "REBOUND": "#d97706",
        "AKUM": "#15803d",
        "DIST": "#b91c1c",
        "SUPER": "#7e22ce",
        "HAKA": "#14b8a6",
        "GC NOW": "#9333ea",
        "WASPADA OB": "#ea580c",
        "WAIT": "#111827"
    }.get(v, "#334155")


def bg_rvol(v):
    if pd.isna(v):
        return "#243244"
    if v >= 250:
        return "#9333ea"
    if v >= 120:
        return "#f97316"
    if v >= 80:
        return "#2563eb"
    return "#374151"


def bg_price(kind):
    return {
        "entry": "#1d4ed8",
        "now": "#2563eb",
        "tp": "#16a34a",
        "sl": "#b91c1c"
    }.get(kind, "#243244")


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
    return {
        "UP": "#16a34a",
        "DEAD": "#dc2626",
        "GOLDEN": "#7c3aed",
        "WAIT": "#111827"
    }.get(v, "#334155")


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
    return {
        "BIG AKUM": "#9333ea",
        "AKUM": "#16a34a",
        "NEUTRAL": "#374151",
        "DIST": "#dc2626",
        "BIG DIST": "#991b1b"
    }.get(v, "#334155")


def bg_trend(v):
    return {
        "BULL": "#16a34a",
        "BEAR": "#dc2626",
        "NEUTRAL": "#6b7280"
    }.get(v, "#334155")


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
        min-width: 1200px;
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
            <th>EMITEN</th>
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
            <th>RSI 5M</th>
            <th>VAL</th>
            <th>FASE</th>
            <th>TREND</th>
          </tr>
        </thead>
        <tbody>
    """)

    for _, row in df.iterrows():
        html += f"""
        <tr>
            <td style="background:#1d4ed8;color:#fff;">{row['symbol']}</td>
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
      <div class="footer-line">AKSI=tindakan trader | SINYAL=kondisi pasar | SL≈1xATR | TP≈2xATR | scan pro mode</div>
    </div>
    </body>
    </html>
    """
    return html


def split_screeners(df: pd.DataFrame):
    day_trading = df.sort_values(by=["score_scalping", "score_total", "rvol"], ascending=False).head(10)
    rebound = df.sort_values(by=["score_bsjp", "score_total", "rsi_5m"], ascending=[False, False, True]).head(10)
    swing = df.sort_values(by=["score_swing", "score_bandar", "score_total"], ascending=False).head(10)
    return day_trading, rebound, swing


# =========================================================
# CHART
# =========================================================
def show_detail_chart(df: pd.DataFrame, symbol_name: str):
    st.subheader(f"Chart Detail: {symbol_name}")

    fig = go.Figure()
    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df["Open"],
        high=df["High"],
        low=df["Low"],
        close=df["Close"],
        name="Candlestick"
    ))
    fig.add_trace(go.Scatter(x=df.index, y=df["MA20"], mode="lines", name="MA20"))
    fig.add_trace(go.Scatter(x=df.index, y=df["MA50"], mode="lines", name="MA50"))
    fig.add_trace(go.Scatter(x=df.index, y=df["BB_UPPER"], mode="lines", name="BB Upper"))
    fig.add_trace(go.Scatter(x=df.index, y=df["BB_LOWER"], mode="lines", name="BB Lower"))
    fig.update_layout(
        height=520,
        template="plotly_dark",
        xaxis_rangeslider_visible=False,
        margin=dict(l=20, r=20, t=40, b=20),
    )
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
# UI
# =========================================================
st.title("HIGH PROB SCREENER IDX PRO")
st.markdown(
    '<div class="small-note">Versi pro: scan paralel, mode strategi, preset filter, progress scan, top picks, dan universe semua emiten IDX atau input manual.</div>',
    unsafe_allow_html=True,
)

with st.sidebar:
    st.header("Mode Scan")
    scan_mode = st.radio(
        "Sumber universe",
        ["Scan semua emiten IDX", "Masukkan daftar emiten manual"],
        index=0
    )

    strategy_mode = st.selectbox(
        "Mode Strategi",
        ["All", "Scalping", "BSJP", "Swing"],
        index=0
    )

    period = st.selectbox("Periode", ["3mo", "6mo", "1y", "2y"], index=1)
    interval = st.selectbox("Interval", ["1d", "1wk"], index=0)

    st.subheader("Preset Filter")
    preset = st.selectbox("Preset", ["Custom", "Conservative", "Aggressive"], index=0)

    default_min_price = 50
    default_min_avg_vol = 100_000
    default_min_value = 1_000_000_000

    if preset == "Conservative":
        default_min_price = 200
        default_min_avg_vol = 300_000
        default_min_value = 3_000_000_000
    elif preset == "Aggressive":
        default_min_price = 50
        default_min_avg_vol = 50_000
        default_min_value = 500_000_000

    st.subheader("Pre-filter Likuiditas")
    min_price = st.number_input("Harga minimum", min_value=1, value=int(default_min_price), step=10)
    min_avg_vol = st.number_input("Rata-rata volume minimum (20 hari)", min_value=0, value=int(default_min_avg_vol), step=50_000)
    min_value = st.number_input("Rata-rata value minimum (Rp, 20 hari)", min_value=0, value=int(default_min_value), step=100_000_000)

    st.subheader("Batas Scan")
    limit_scan = st.number_input("Maksimum emiten diproses", min_value=20, value=200, step=20)
    top_n = st.number_input("Jumlah kandidat terbaik", min_value=5, value=20, step=5)
    max_workers = st.number_input("Parallel workers", min_value=2, value=10, step=1)

    manual_symbols = st.text_area(
        "Daftar emiten manual (pisahkan koma)",
        value="BBCA,BBRI,BMRI,TLKM,ASII",
        height=120,
        disabled=(scan_mode == "Scan semua emiten IDX"),
    )

    auto_refresh = st.checkbox("Auto Refresh 60 detik", value=False)
    run_btn = st.button("Jalankan Scan Pro", use_container_width=True)

if run_btn or "scan_result_df" not in st.session_state:
    with st.spinner("Menyiapkan universe dan scan pro..."):
        if scan_mode == "Scan semua emiten IDX":
            universe = get_all_idx_symbols()
        else:
            universe = [normalize_jk_symbol(x) for x in manual_symbols.split(",") if x.strip()]
            universe = [x for x in universe if x]

        result_df, scanned, passed_prefilter = run_screener_pro(
            universe,
            period=period,
            interval=interval,
            min_price=min_price,
            min_avg_vol=min_avg_vol,
            min_value=min_value,
            limit_scan=int(limit_scan),
            max_workers=int(max_workers),
        )

        result_df = sort_by_strategy(result_df, strategy_mode)

        st.session_state["scan_result_df"] = result_df
        st.session_state["scan_meta"] = {
            "universe_count": len(universe),
            "scanned": scanned,
            "passed_prefilter": passed_prefilter,
            "strategy_mode": strategy_mode,
        }

screener_df = st.session_state.get("scan_result_df", pd.DataFrame())
meta = st.session_state.get("scan_meta", {})

if screener_df.empty:
    st.error("Belum ada kandidat yang lolos. Turunkan filter atau perbesar batas scan.")
    st.stop()

best_df = screener_df.head(int(top_n))
day_df, rebound_df, swing_df = split_screeners(best_df)

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Universe", meta.get("universe_count", 0))
c2.metric("Diproses", meta.get("scanned", 0))
c3.metric("Lolos Filter", meta.get("passed_prefilter", 0))
c4.metric("Mode", meta.get("strategy_mode", "-"))
c5.metric("Top Pick", best_df.iloc[0]["symbol"])

st.subheader("🔥 Top Picks Hari Ini")
top3 = best_df.head(3)
for idx, (_, row) in enumerate(top3.iterrows(), start=1):
    st.success(f"#{idx} {row['symbol']} | Score {int(row['score_total'])} | Sinyal {row['sinyal']} | Trend {row['trend']}")

components.html(
    make_html_table(day_df, "TOP DAY TRADING PICKS", "Momentum cepat | breakout | RVOL | RSI 5M | ATR"),
    height=420,
    scrolling=True
)
components.html(
    make_html_table(rebound_df, "TOP BSJP / REBOUND PICKS", "Buy saat jenuh penurunan | support | lower band | early rebound"),
    height=420,
    scrolling=True
)
components.html(
    make_html_table(swing_df, "TOP SWING / TREND PICKS", "Trend menengah | MA20/MA50 | MACD | akumulasi price-volume"),
    height=420,
    scrolling=True
)

st.subheader("Ranking Kandidat Terbaik")
rank_df = best_df[[
    "symbol", "gain", "rvol", "rsi_5m", "fase", "trend",
    "score_scalping", "score_bsjp", "score_swing", "score_bandar", "score_total"
]].copy()
rank_df.columns = [
    "EMITEN", "GAIN", "RVOL", "RSI 5M", "FASE", "TREND",
    "SCALPING", "BSJP", "SWING", "BANDAR", "TOTAL"
]
st.dataframe(rank_df, use_container_width=True)

selected_symbol = st.selectbox("Pilih saham untuk detail", best_df["full_symbol"].tolist())
selected_row = best_df[best_df["full_symbol"] == selected_symbol].iloc[0]
selected_df = selected_row["daily_df"]

d1, d2, d3, d4, d5 = st.columns(5)
d1.metric("EMITEN", selected_row["symbol"])
d2.metric("GAIN", fmt_pct(selected_row["gain"]))
d3.metric("RVOL", fmt_pct(selected_row["rvol"]))
d4.metric("RSI 5M", rsi_cell_text(selected_row["rsi_5m"]))
d5.metric("VAL", human_value(selected_row["val"]))

show_detail_chart(selected_df, selected_row["symbol"])

st.subheader("Analisa Strategi")
t1, t2, t3, t4 = st.tabs(["1. Scalping", "2. BSJP", "3. Swing", "4. Bandarmologi"])

with t1:
    st.write("Logika: momentum cepat, EMA9/MA20, volume aktif, breakout, risk/reward, dan likuiditas.")
    st.metric("Skor Scalping", int(selected_row["score_scalping"]))
    st.write(f"Aksi: **{selected_row['aksi']}**")
    st.write(f"Sinyal: **{selected_row['sinyal']}**")
    st.write(f"Entry: **{fmt_price(selected_row['entry'])}**")
    st.write(f"TP: **{fmt_price(selected_row['tp'])}**")
    st.write(f"SL: **{fmt_price(selected_row['sl'])}**")

with t2:
    st.write("Logika: buy saat jenuh penurunan, dekat support/lower band, mulai muncul rebound.")
    st.metric("Skor BSJP", int(selected_row["score_bsjp"]))
    st.write(f"RSI 5M: **{rsi_cell_text(selected_row['rsi_5m'])}**")
    st.write(f"Fase: **{selected_row['fase']}**")

with t3:
    st.write("Logika: trend menengah, MA20/MA50, MACD, volume, posisi harga, dan liquidity bonus.")
    st.metric("Skor Swing", int(selected_row["score_swing"]))
    st.write(f"Trend: **{selected_row['trend']}**")
    st.write(f"% To TP: **{fmt_pct(selected_row['to_tp'])}**")

with t4:
    st.write("Logika: proxy bandarmologi dari akumulasi/distribusi berbasis harga-volume.")
    st.metric("Skor Bandarmologi", int(selected_row["score_bandar"]))
    st.write(f"Fase: **{selected_row['fase']}**")
    st.write(f"Value transaksi: **{human_value(selected_row['val'])}**")

st.caption("Universe saham diambil dari daftar saham IDX resmi bila mode scan semua dipilih. Harga dan volume teknikal pada app ini memakai yfinance, jadi ini cocok untuk screening kandidat, bukan feed eksekusi real-time penuh.")

if auto_refresh:
    time.sleep(60)
    st.rerun()
