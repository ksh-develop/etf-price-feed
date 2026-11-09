"""ETF 종가 수집: yfinance(야후) -> Stooq 순으로 시도하고 data/ 에 저장."""
import csv, io, json, os, datetime as dt
import requests

TICKERS = ["SPY", "VOO", "SPYM", "SSO", "UPRO", "SPXL", "QQQ", "QQQM", "QLD", "TQQQ"]
DATA = "data"; DAILY = os.path.join(DATA, "daily")
os.makedirs(DAILY, exist_ok=True)
UA = {"User-Agent": "etf-price-feed/1.0"}

def load(t):
    p = os.path.join(DAILY, f"{t}.csv")
    if not os.path.exists(p): return {}
    with open(p) as f: return {r["date"]: r for r in csv.DictReader(f)}

def save(t, rows):
    p = os.path.join(DAILY, f"{t}.csv")
    with open(p, "w", newline="") as f:
        w = csv.DictWriter(f, ["date", "open", "high", "low", "close", "volume", "source"])
        w.writeheader()
        for d in sorted(rows): w.writerow(rows[d])

def r2(x): return f"{float(x):.4f}".rstrip("0").rstrip(".")

def from_yahoo(t, period):
    import yfinance as yf
    df = yf.Ticker(t).history(period=period, interval="1d", auto_adjust=False, actions=False)
    out = {}
    for idx, r in df.iterrows():
        if r.isna()[["Open", "High", "Low", "Close"]].any(): continue
        d = idx.strftime("%Y-%m-%d")
        out[d] = dict(date=d, open=r2(r.Open), high=r2(r.High), low=r2(r.Low), close=r2(r.Close),
                      volume=int(r.Volume or 0), source="yahoo")
    return out

def from_stooq(t):
    url = f"https://stooq.com/q/d/l/?s={t.lower()}.us&i=d"
    txt = requests.get(url, headers=UA, timeout=20).text
    if not txt.startswith("Date"): raise RuntimeError("stooq: " + txt[:60])
    out = {}
    for r in csv.DictReader(io.StringIO(txt)):
        d = r["Date"]
        out[d] = dict(date=d, open=r2(r["Open"]), high=r2(r["High"]), low=r2(r["Low"]), close=r2(r["Close"]),
                      volume=int(float(r.get("Volume") or 0)), source="stooq")
    return out

def fx():
    try:
        import yfinance as yf
        df = yf.Ticker("KRW=X").history(period="5d", interval="1d")
        if len(df): return dict(rate=round(float(df.Close.iloc[-1]), 2), date=df.index[-1].strftime("%Y-%m-%d"), source="yahoo")
    except Exception as e: print("fx yahoo fail", e)
    try:
        j = requests.get("https://open.er-api.com/v6/latest/USD", headers=UA, timeout=20).json()
        return dict(rate=round(j["rates"]["KRW"], 2), date=dt.datetime.utcfromtimestamp(j["time_last_update_unix"]).strftime("%Y-%m-%d"), source="open.er-api")
    except Exception as e: print("fx er-api fail", e)
    return None

latest, errors = {}, []
for t in TICKERS:
    rows = load(t)
    period = "max" if len(rows) < 100 else "1mo"   # 첫 실행: 상장일부터 전체
    new = {}
    for name, fn in (("yahoo", lambda: from_yahoo(t, period)), ("stooq", lambda: from_stooq(t))):
        try:
            new = fn()
            if new: break
        except Exception as e:
            errors.append(f"{t} {name}: {e}"); print(t, name, "fail", e)
    if name == "stooq" and len(rows) >= 100:   # 히스토리가 있으면 최근 30일만 반영
        cut = (dt.date.today() - dt.timedelta(days=30)).isoformat()
        new = {d: r for d, r in new.items() if d >= cut}
    rows.update(new)
    if rows: save(t, rows)
    last = rows[max(rows)] if rows else None
    if last: latest[t] = {k: (float(v) if k in ("open", "high", "low", "close") else v) for k, v in last.items()}

dates = [v["date"] for v in latest.values()]
out = {
    "generated_at": dt.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
    "as_of": min(dates) if dates else None,
    "complete": len(latest) == len(TICKERS) and len(set(dates)) == 1,
    "prices": latest,
    "usdkrw": fx(),
    "errors": errors,
}
with open(os.path.join(DATA, "latest.json"), "w") as f: json.dump(out, f, ensure_ascii=False, indent=1)
print(json.dumps(out, ensure_ascii=False, indent=1))
