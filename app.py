import os
import math
import asyncio
from dataclasses import dataclass
from typing import List, Dict, Optional

import numpy as np
import pandas as pd
import yfinance as yf
from telegram import Bot


# =========================
# CONFIG
# =========================
WATCHLIST = [
    "GOTO.JK", "BUKA.JK", "BRIS.JK", "ANTM.JK", "ESSA.JK",
    "TINS.JK", "ADMR.JK", "ERAA.JK", "TMAS.JK", "WIKA.JK",
]

MAX_PRICE = 1000
DAILY_PERIOD = "6mo"
INTRADAY_PERIOD = "1mo"
DAILY_INTERVAL = "1d"
INTRADAY_INTERVAL = "1h"  # bisa diganti 30m kalau datanya tersedia
MIN_AVG_VALUE = 1_000_000_000  # filter likuiditas kasar
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")


# =========================
# INDICATORS
# =========================
def ema(series: pd.Series, span: int) -> pd.Series:
    return series.ewm(span=span, adjust=False).mean()


def rsi(series: pd.Series, period: int = 14) -> pd.Series:
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    out = 100 - (100 / (1 + rs))
    return out.fillna(50)


def atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
    high_low = df["High"] - df["Low"]
    high_close = (df["High"] - df["Close"].shift()).abs()
    low_close = (df["Low"] - df["Close"].shift()).abs()
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    return tr.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()


def rolling_breakout_high(series: pd.Series, lookback: int = 20) -> pd.Series:
    return series.shift(1).rolling(lookback).max()


# =========================
# DATA LOADER
# =========================
def load_data(symbol: str, period: str, interval: str) -> Optional[pd.DataFrame]:
    try:
        df = yf.download(symbol, period=period, interval=interval, auto_adjust=False, progress=False)
        if df is None or df.empty:
            return None
        df = df.dropna().copy()
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        return df
    except Exception:
        return None


# =========================
# SCORING ENGINE
# =========================
@dataclass
class ScreenResult:
    symbol: str
    price: float
    gain_pct: float
    signal: str
    action: str
    score: int
    probability: str
    entry: float
    tp1: float
    tp2: float
    sl: float
    profit_pct_tp1: float
    rsi_daily: float
    rsi_intraday: float
    vol_ratio: float
    value_trade: float
    phase: str
    trend: str
    note: str


def prepare_indicators(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["ema20"] = ema(out["Close"], 20)
    out["ema50"] = ema(out["Close"], 50)
    out["ema200"] = ema(out["Close"], 200)
    out["rsi14"] = rsi(out["Close"], 14)
    out["atr14"] = atr(out, 14)
    out["vol_ma20"] = out["Volume"].rolling(20).mean()
    out["value"] = out["Close"] * out["Volume"]
    out["value_ma20"] = out["value"].rolling(20).mean()
    out["breakout20"] = rolling_breakout_high(out["High"], 20)
    return out


def classify_trend(last: pd.Series) -> str:
    if last["Close"] > last["ema20"] > last["ema50"] > last["ema200"]:
        return "BULL STRONG"
    if last["Close"] > last["ema20"] > last["ema50"]:
        return "BULL"
    if last["Close"] < last["ema20"] < last["ema50"]:
        return "BEAR"
    return "NEUTRAL"


def classify_phase(last: pd.Series) -> str:
    if last["Close"] > last["breakout20"]:
        return "BREAKOUT"
    distance = abs(last["Close"] - last["ema20"]) / max(last["Close"], 1e-9)
    if distance <= 0.03 and last["ema20"] > last["ema50"]:
        return "PULLBACK"
    if last["Volume"] > 1.8 * last["vol_ma20"]:
        return "MOMENTUM"
    return "BASE"


def score_daily(daily: pd.DataFrame) -> Dict[str, float]:
    last = daily.iloc[-1]
    prev = daily.iloc[-2]
    score = 0
    notes = []

    if last["Close"] <= MAX_PRICE:
        score += 10
        notes.append("harga<=1000")
    else:
        notes.append("harga>1000")

    if last["ema20"] > last["ema50"]:
        score += 15
        notes.append("ema20>ema50")

    if last["Close"] > last["ema20"]:
        score += 10
        notes.append("close>ema20")

    if last["Close"] > last["breakout20"]:
        score += 20
        notes.append("breakout20")

    if 52 <= last["rsi14"] <= 72:
        score += 15
        notes.append("rsi sehat")
    elif 45 <= last["rsi14"] < 52:
        score += 8
        notes.append("rsi pullback")

    vol_ratio = float(last["Volume"] / last["vol_ma20"]) if last["vol_ma20"] and not math.isnan(last["vol_ma20"]) else 0
    if vol_ratio >= 2.0:
        score += 20
        notes.append("volume x2")
    elif vol_ratio >= 1.5:
        score += 12
        notes.append("volume spike")

    avg_value = float(last["value_ma20"]) if not math.isnan(last["value_ma20"]) else 0
    if avg_value >= MIN_AVG_VALUE:
        score += 10
        notes.append("likuid")

    gain_pct = ((last["Close"] / prev["Close"]) - 1) * 100

    return {
        "score": score,
        "gain_pct": gain_pct,
        "vol_ratio": vol_ratio,
        "avg_value": avg_value,
        "notes": ", ".join(notes),
    }


def score_intraday(intra: pd.DataFrame) -> Dict[str, float]:
    last = intra.iloc[-1]
    score = 0
    notes = []

    if last["Close"] > last["ema20"]:
        score += 10
        notes.append("intra close>ema20")
    if last["ema20"] > last["ema50"]:
        score += 10
        notes.append("intra ema20>ema50")
    if 55 <= last["rsi14"] <= 75:
        score += 10
        notes.append("intra rsi sehat")

    vol_ratio = float(last["Volume"] / last["vol_ma20"]) if last["vol_ma20"] and not math.isnan(last["vol_ma20"]) else 0
    if vol_ratio >= 1.5:
        score += 10
        notes.append("intra vol spike")

    return {
        "score": score,
        "vol_ratio": vol_ratio,
        "notes": ", ".join(notes),
    }


def probability_label(score: int) -> str:
    if score >= 80:
        return "A+"
    if score >= 65:
        return "A"
    if score >= 50:
        return "B"
    return "C"


def decide_signal(daily: pd.DataFrame, intra: pd.DataFrame, total_score: int) -> str:
    d = daily.iloc[-1]
    i = intra.iloc[-1]

    day_trade = (
        d["Close"] > d["ema20"] and
        d["ema20"] > d["ema50"] and
        i["Close"] > i["ema20"] and
        55 <= i["rsi14"] <= 75 and
        total_score >= 55
    )

    swing = (
        d["ema20"] > d["ema50"] and
        45 <= d["rsi14"] <= 68 and
        abs(d["Close"] - d["ema20"]) / max(d["Close"], 1e-9) <= 0.04 and
        total_score >= 50
    )

    if day_trade and swing:
        return "DAY+SWING"
    if day_trade:
        return "DAY TRADE"
    if swing:
        return "SWING"
    return "WAIT"


def build_result(symbol: str, daily: pd.DataFrame, intra: pd.DataFrame) -> Optional[ScreenResult]:
    dlast = daily.iloc[-1]
    ilast = intra.iloc[-1]

    if float(dlast["Close"]) > MAX_PRICE:
        return None

    daily_score = score_daily(daily)
    intra_score = score_intraday(intra)
    total_score = int(daily_score["score"] + intra_score["score"])

    signal = decide_signal(daily, intra, total_score)
    action = "AT ENTRY" if signal != "WAIT" else "WAIT"

    current_price = float(dlast["Close"])
    current_atr = float(dlast["atr14"]) if not math.isnan(dlast["atr14"]) else current_price * 0.03

    entry = current_price
    sl = max(current_price - 1.5 * current_atr, current_price * 0.94)
    tp1 = current_price + 1.5 * current_atr
    tp2 = current_price + 3.0 * current_atr
    profit_pct_tp1 = ((tp1 / entry) - 1) * 100

    return ScreenResult(
        symbol=symbol,
        price=round(current_price, 2),
        gain_pct=round(float(daily_score["gain_pct"]), 2),
        signal=signal,
        action=action,
        score=total_score,
        probability=probability_label(total_score),
        entry=round(entry, 2),
        tp1=round(tp1, 2),
        tp2=round(tp2, 2),
        sl=round(sl, 2),
        profit_pct_tp1=round(profit_pct_tp1, 2),
        rsi_daily=round(float(dlast["rsi14"]), 1),
        rsi_intraday=round(float(ilast["rsi14"]), 1),
        vol_ratio=round(max(float(daily_score["vol_ratio"]), float(intra_score["vol_ratio"])), 2),
        value_trade=round(float(daily_score["avg_value"]), 0),
        phase=classify_phase(dlast),
        trend=classify_trend(dlast),
        note=f"D: {daily_score['notes']} | I: {intra_score['notes']}",
    )


# =========================
# OUTPUT TABLE
# =========================
def screen_symbols(symbols: List[str]) -> pd.DataFrame:
    rows = []
    for symbol in symbols:
        daily_raw = load_data(symbol, DAILY_PERIOD, DAILY_INTERVAL)
        intra_raw = load_data(symbol, INTRADAY_PERIOD, INTRADAY_INTERVAL)
        if daily_raw is None or intra_raw is None:
            continue
        if len(daily_raw) < 60 or len(intra_raw) < 60:
            continue

        daily = prepare_indicators(daily_raw)
        intra = prepare_indicators(intra_raw)
        result = build_result(symbol, daily, intra)
        if result is None:
            continue
        rows.append(result.__dict__)

    if not rows:
        return pd.DataFrame()

    df = pd.DataFrame(rows)
    df = df.sort_values(by=["score", "gain_pct"], ascending=[False, False]).reset_index(drop=True)
    return df


def format_terminal_table(df: pd.DataFrame) -> str:
    if df.empty:
        return "Tidak ada kandidat yang lolos filter."

    show = df[[
        "symbol", "gain_pct", "action", "signal", "score", "probability",
        "entry", "tp1", "sl", "profit_pct_tp1", "rsi_daily", "rsi_intraday",
        "vol_ratio", "phase", "trend"
    ]].copy()

    show.columns = [
        "EMITEN", "GAIN%", "AKSI", "SINYAL", "SCORE", "HP",
        "ENTRY", "TP", "SL", "%TP", "RSI D", "RSI I",
        "VOL", "FASE", "TREND"
    ]
    return show.to_string(index=False)


def format_telegram_message(df: pd.DataFrame, top_n: int = 10) -> str:
    if df.empty:
        return "📭 Tidak ada kandidat high probability saat ini."

    lines = ["📊 HIGH PROBABILITY SCREENER"]
    lines.append(f"Filter harga ≤ {MAX_PRICE}")
    lines.append("")

    for _, row in df.head(top_n).iterrows():
        lines.append(
            f"{row['symbol']} | {row['signal']} | Score {row['score']} ({row['probability']})\n"
            f"Price {row['price']} | Gain {row['gain_pct']}% | Trend {row['trend']}\n"
            f"Entry {row['entry']} | TP1 {row['tp1']} | SL {row['sl']}\n"
            f"RSI D/I {row['rsi_daily']}/{row['rsi_intraday']} | Vol x{row['vol_ratio']} | {row['phase']}"
        )
        lines.append("-" * 28)

    msg = "\n".join(lines)
    return msg[:4000]


# =========================
# TELEGRAM
# =========================
async def send_telegram(message: str) -> None:
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("Telegram token/chat id belum di-set.")
        return
    bot = Bot(token=TELEGRAM_TOKEN)
    await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)


# =========================
# MAIN
# =========================
def main() -> None:
    df = screen_symbols(WATCHLIST)
    print(format_terminal_table(df))

    if not df.empty:
        df.to_csv("screener_output.csv", index=False)
        msg = format_telegram_message(df, top_n=8)
        asyncio.run(send_telegram(msg))


if __name__ == "__main__":
    main()
