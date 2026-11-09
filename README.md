# etf-price-feed
S&P·나스닥 분리 트리거 전략용 종가 피드. GitHub Actions가 평일 미국 장 마감 후(06:40·07:40·08:10 KST) 실행됩니다.

- `data/latest.json` — 최신 거래일의 SPY·VOO·SPYM·SSO·UPRO·SPXL·QQQ·QQQM·QLD·TQQQ 시가/고가/저가/종가, USD/KRW, 출처
- `data/daily/<TICKER>.csv` — 상장일부터 전체 일봉 (분할만 반영, 배당 미반영)

출처 순서: 야후(yfinance) → Stooq. 수동 실행: Actions 탭 → fetch-prices → Run workflow.
