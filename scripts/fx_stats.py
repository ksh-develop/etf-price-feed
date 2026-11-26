"""원/달러 기간별 평균 환율: data/fx_usdkrw.csv -> data/fx_stats.json

최근 1·3·5·10년 동안의 일별 종가(야후 KRW=X)를 단순 평균하고, 최저·최고와
최근 10년 월평균 시계열을 함께 저장한다. fetch.py 끝에서 자동 실행되며 따로 실행해도 된다.
"""
import csv, json, os, datetime as dt

DATA = "data"
SRC = os.path.join(DATA, "fx_usdkrw.csv")
OUT = os.path.join(DATA, "fx_stats.json")
YEARS = (1, 3, 5, 10)


def years_before(d, n):
    try:
        return d.replace(year=d.year - n)
    except ValueError:            # 2월 29일
        return d.replace(year=d.year - n, day=28)


def main():
    with open(SRC) as f:
        rows = [(dt.date.fromisoformat(r["date"]), float(r["close"])) for r in csv.DictReader(f) if r.get("close")]
    rows.sort()
    if not rows:
        raise SystemExit("fx_usdkrw.csv 비어 있음")
    last_d, last_v = rows[-1]

    periods = []
    for n in YEARS:
        start = years_before(last_d, n)
        win = [(d, v) for d, v in rows if d > start]
        if not win:
            continue
        vals = [v for _, v in win]
        lo = min(win, key=lambda x: x[1]); hi = max(win, key=lambda x: x[1])
        avg = sum(vals) / len(vals)
        periods.append({
            "years": n,
            "label": f"최근 {n}년",
            "from": win[0][0].isoformat(), "to": last_d.isoformat(), "days": len(vals),
            "avg": round(avg, 2),
            "min": round(lo[1], 2), "min_date": lo[0].isoformat(),
            "max": round(hi[1], 2), "max_date": hi[0].isoformat(),
            "vs_avg_pct": round((last_v / avg - 1) * 100, 2),   # 현재 환율이 평균보다 몇 % 높은지
        })

    # 최근 10년 월평균 (차트용)
    start10 = years_before(last_d, 10)
    acc = {}
    for d, v in rows:
        if d > start10:
            acc.setdefault(d.strftime("%Y-%m"), []).append(v)
    monthly = [[m, round(sum(vs) / len(vs), 2)] for m, vs in sorted(acc.items())]

    out = {
        "generated_at": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "as_of": last_d.isoformat(),
        "latest": round(last_v, 2),
        "method": "야후 KRW=X 일별 종가의 단순 평균 (기준일 포함, 기준일로부터 N년 전 다음 날부터)",
        "source": "data/fx_usdkrw.csv",
        "periods": periods,
        "monthly": monthly,
    }
    with open(OUT, "w") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    for p in periods:
        print(f"{p['label']}: 평균 {p['avg']:,.2f}원 (최저 {p['min']:,.2f} {p['min_date']} · 최고 {p['max']:,.2f} {p['max_date']}, {p['days']}일)")
    print(f"현재 {last_v:,.2f}원 ({last_d})")


if __name__ == "__main__":
    main()
