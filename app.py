import os
import math
import asyncio
import time
from typing import List, Optional

import numpy as np
import pandas as pd
import yfinance as yf
from telegram import Bot


# =====================================================
# CONFIG
# =====================================================
WATCHLIST = [
    "AADI.JK", "AKRA.JK", "ANTM.JK", "ASSA.JK", "BBYB.JK",
    "BRIS.JK", "BUKA.JK", "CPIN.JK", "DOID.JK", "ELSA.JK",
    "ERAA.JK", "ESSA.JK", "GOTO.JK", "HEAL.JK", "HRUM.JK",
    "INCO.JK", "JPFA.JK", "MEDC.JK", "PGEO.JK", "PTBA.JK",
    "PWON.JK", "RMKE.JK", "SCMA.JK", "SIDO.JK", "SMDR.JK",
    "SMRA.JK", "TMAS.JK", "TOWR.JK", "WIKA.JK", "WSKT.JK",
    "ZINC.JK", "BIRD.JK", "MAPI.JK", "ADMR.JK", "DEWA.JK",
    "ENRG.JK", "EXCL.JK", "ISAT.JK", "MNCN.JK", "TINS.JK"
]

MAX_PRICE = 1000
DAILY_PERIOD = "8mo"
INTRADAY_PERIOD = "1mo"
DAILY_INTERVAL = "1d"
INTRADAY_INTERVAL = "1h"
TOP_N_TELEGRAM = 20
REFRESH_SECONDS = 60
EXPORT_CSV = "bsjp_screener_single_table.csv"


# =====================================================
# INDICATORS
# =====================================================
def ema(series: pd.Series, span: int) -> pd.Series:
    return series.ewm(span=span, adjust=False).mean()


def rsi(series: pd.Series, period: int = 14) -> pd.Series:
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    return (100 - (100 / (1 + rs))).fillna(50)


def atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
    high_low = df["High"] - df["Low"]
    high_close = (df["High"] - df["Close"].shift()).abs()
    low_close = (df["Low"] - df["Close"].shift()).abs()
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    return tr.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()


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


def prepare(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["ema20"] = ema(out["Close"], 20)
    out["ema50"] = ema(out["Close"], 50)
    out["ema200"] = ema(out["Close"], 200)
    out["rsi14"] = rsi(out["Close"], 14)
    out["atr14"] = atr(out, 14)
    out["vol_ma20"] = out["Volume"].rolling(20).mean()
    out["value"] = out["Close"] * out["Volume"]
    out["value_ma20"] = out["value"].rolling(20).mean()
    out["high20"] = out["High"].shift(1).rolling(20).max()
    out["chg_pct"] = out["Close"].pct_change() * 100
    out["wick_pct"] = ((out["High"] - out[["Open", "Close"]].max(axis=1)) / out["Close"].replace(0, np.nan) * 100).fillna(0)
    return out


# =====================================================
# SCREENER LOGIC
# =====================================================
def trend_label(last: pd.Series) -> str:
    if last["Close"] > last["ema20"] > last["ema50"] > last["ema200"]:
        return "BULL STRONG"
    if last["Close"] > last["ema20"] > last["ema50"]:
        return "BULL"
    if last["Close"] < last["ema20"] < last["ema50"]:
        return "BEAR"
    return "NEUTRAL"


def phase_label(last: pd.Series) -> str:
    if last["Close"] > last["high20"]:
        return "BREAKOUT"
    if abs(last["Close"] - last["ema20"]) / max(last["Close"], 1e-9) <= 0.03 and last["ema20"] > last["ema50"]:
        return "AKUM"
    if last["Volume"] > 1.8 * last["vol_ma20"]:
        return "MOMENTUM"
    if last["Close"] < last["ema20"] and last["rsi14"] > 65:
        return "DISTRIBUSI"
    return "NEUTRAL"


def signal_label(d: pd.Series, i: pd.Series) -> str:
    breakout = d["Close"] > d["high20"] and d["Volume"] > 1.5 * d["vol_ma20"]
    rebound = d["Close"] > d["ema20"] and d["chg_pct"] > 0 and d["rsi14"] >= 50
    pullback = abs(d["Close"] - d["ema20"]) / max(d["Close"], 1e-9) <= 0.025 and d["ema20"] > d["ema50"]
    intraday_ok = i["Close"] > i["ema20"] and i["ema20"] > i["ema50"] and i["rsi14"] >= 55

    if breakout and intraday_ok:
        return "BREAKOUT"
    if rebound and intraday_ok:
        return "ON TRACK"
    if pullback and d["rsi14"] >= 45:
        return "AKUM"
    if d["rsi14"] > 72:
        return "WASPADA OB"
    if d["Close"] < d["ema20"] and d["rsi14"] < 45:
        return "DIST A"
    return "WAIT"


def action_label(signal: str, i: pd.Series) -> str:
    if signal in {"BREAKOUT", "ON TRACK", "AKUM"}:
        return "AT ENTRY" if i["Close"] >= i["ema20"] else "WAIT GC"
    if signal == "WASPADA OB":
        return "HOLD"
    return "WAIT"


def probability_score(d: pd.Series, i: pd.Series) -> int:
    score = 0
    if d["Close"] <= MAX_PRICE:
        score += 10
    if d["ema20"] > d["ema50"]:
        score += 15
    if d["Close"] > d["ema20"]:
        score += 10
    if d["Close"] > d["high20"]:
        score += 20
    if 50 <= d["rsi14"] <= 70:
        score += 10
    if d["Volume"] > 1.5 * d["vol_ma20"]:
        score += 15
    if i["ema20"] > i["ema50"]:
        score += 10
    if i["Close"] > i["ema20"]:
        score += 5
    if 55 <= i["rsi14"] <= 75:
        score += 5
    return int(score)


def rvol_percent(d: pd.Series) -> float:
    if d["vol_ma20"] and not math.isnan(d["vol_ma20"]):
        return round(float(d["Volume"] / d["vol_ma20"] * 100), 0)
    return 0.0


def tp_sl(last: pd.Series) -> tuple[float, float, float]:
    entry = float(last["Close"])
    atr_value = float(last["atr14"]) if not math.isnan(last["atr14"]) else entry * 0.03
    tp = entry + 2.0 * atr_value
    sl = max(entry - 1.2 * atr_value, entry * 0.94)
    return round(entry, 2), round(tp, 2), round(sl, 2)


def normalize_symbol(symbol: str) -> str:
    symbol = symbol.strip().upper()
    if not symbol:
        return ""
    return symbol if symbol.endswith(".JK") else f"{symbol}.JK"


def search_emitens(query: str, symbols: List[str]) -> List[str]:
    query = query.strip().upper()
    if not query:
        return symbols
    matched = []
    for symbol in symbols:
        base = symbol.replace(".JK", "")
        if query in base:
            matched.append(symbol)
    return matched


def row_from_symbol(symbol: str) -> Optional[dict]:
    daily_raw = load_data(symbol, DAILY_PERIOD, DAILY_INTERVAL)
    intra_raw = load_data(symbol, INTRADAY_PERIOD, INTRADAY_INTERVAL)
    if daily_raw is None or intra_raw is None:
        return None
    if len(daily_raw) < 80 or len(intra_raw) < 60:
        return None

    daily = prepare(daily_raw)
    intra = prepare(intra_raw)
    d = daily.iloc[-1]
    i = intra.iloc[-1]
    prev = daily.iloc[-2]

    price = float(d["Close"])
    if price > MAX_PRICE:
        return None

    signal = signal_label(d, i)
    action = action_label(signal, i)
    entry, tp, sl = tp_sl(d)
    score = probability_score(d, i)
    gain = ((price / float(prev["Close"])) - 1) * 100
    profit_pct = ((tp / entry) - 1) * 100 if entry else 0
    trend = trend_label(d)
    phase = phase_label(d)
    rsi_sig = "UP" if d["rsi14"] >= 50 else "DEAD"

    return {
        "EMITEN": symbol.replace(".JK", ""),
        "GAIN": round(gain, 1),
        "WICK": round(float(d["wick_pct"]), 1),
        "AKSI": action,
        "SINYAL": signal,
        "RVOL": rvol_percent(d),
        "ENTRY": entry,
        "NOW": round(price, 2),
        "TP": tp,
        "SL": sl,
        "PROFIT": round(((price / entry) - 1) * 100 if entry else 0, 1),
        "%TO TP": round(profit_pct, 1),
        "RSI SIG": rsi_sig,
        "RSI 5M": round(float(i["rsi14"]), 1),
        "VAL": round(float(d["value_ma20"]) / 1_000_000, 1) if not math.isnan(d["value_ma20"]) else 0,
        "FASE": phase,
        "TREND": trend,
        "SCORE": score,
    }


def build_single_table(symbols: List[str]) -> pd.DataFrame:
    rows = []
    seen = set()
    for symbol in symbols:
        symbol = normalize_symbol(symbol)
        if not symbol or symbol in seen:
            continue
        seen.add(symbol)
        row = row_from_symbol(symbol)
        if row:
            rows.append(row)

    if not rows:
        return pd.DataFrame()

    df = pd.DataFrame(rows)
    df = df.sort_values(by=["SCORE", "RVOL", "GAIN"], ascending=[False, False, False]).reset_index(drop=True)
    return df


# =====================================================
# DISPLAY
# =====================================================
def print_table(df: pd.DataFrame) -> None:
    os.system("cls" if os.name == "nt" else "clear")
    print(f"BSJP SCREENER | harga <= {MAX_PRICE} | auto refresh {REFRESH_SECONDS} detik")
    print(time.strftime("Update terakhir: %Y-%m-%d %H:%M:%S"))
    print("=" * 120)

    if df.empty:
        print("Tidak ada emiten yang lolos filter.")
        return

    cols = [
        "EMITEN", "GAIN", "WICK", "AKSI", "SINYAL", "RVOL",
        "ENTRY", "NOW", "TP", "SL", "PROFIT", "%TO TP",
        "RSI SIG", "RSI 5M", "VAL", "FASE", "TREND"
    ]
    print(df[cols].to_string(index=False))




    lines = [f"📊 BSJP SCREENER | Harga <= {MAX_PRICE}", ""]
    for _, row in df.head(TOP_N_TELEGRAM).iterrows():
        lines.append(
            f"{row['EMITEN']} | {row['SINYAL']} | {row['AKSI']}
"
            f"Now {row['NOW']} | Entry {row['ENTRY']} | TP {row['TP']} | SL {row['SL']}
"
            f"Gain {row['GAIN']}% | RVOL {row['RVOL']}% | RSI5M {row['RSI 5M']} | {row['TREND']}"
        )
        lines.append("-" * 26)
    return "
".join(lines)[:4000]


# =====================================================
# INTERACTIVE + AUTO REFRESH
# =====================================================
def resolve_symbols_from_input(user_input: str) -> List[str]:
    user_input = user_input.strip()
    if not user_input or user_input.lower() == "all":
        return WATCHLIST

    if "," in user_input:
        return [normalize_symbol(x) for x in user_input.split(",") if normalize_symbol(x)]

    matches = search_emitens(user_input, WATCHLIST)
    if matches:
        return matches

    single = normalize_symbol(user_input)
    return [single] if single else WATCHLIST


def run_once(symbols: List[str], send_telegram: bool = False) -> pd.DataFrame:
    df = build_single_table(symbols)
    print_table(df)
    if not df.empty:
        df.to_csv(EXPORT_CSV, index=False)



def auto_refresh_loop(symbols: List[str], send_telegram: bool = False) -> None:
    while True:
        try:
            run_once(symbols, send_telegram=send_telegram)
        except KeyboardInterrupt:
            print("
Auto refresh dihentikan.")
            break
        except Exception as exc:
            print(f"Error: {exc}")
        time.sleep(REFRESH_SECONDS)


def main() -> None:
    print("=== BSJP Screener ===")
    print("Ketik 'all' untuk semua watchlist")
    print("Ketik kode saham, contoh: GOTO")
    print("Ketik beberapa kode dengan koma, contoh: GOTO,BUKA,BRIS")
    print("Ketik sebagian nama untuk search, contoh: GO")
    print("")

    user_input = input("Cari emiten: ").strip()
    symbols = resolve_symbols_from_input(user_input)

    if not symbols:
        print("Emiten tidak ditemukan.")
        return

    print(f"Memantau: {', '.join([s.replace('.JK', '') for s in symbols])}")
    choice = input("Aktifkan auto refresh 60 detik? (y/n): ").strip().lower()
    

    if choice == "y":
        auto_refresh_loop(symbols, send_telegram=send_telegram)
    else:
        run_once(symbols, send_telegram=send_telegram)


if __name__ == "__main__":
    main()
