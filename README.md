# etf-price-feed
S&P·나스닥 분리 트리거 전략용 종가 피드. GitHub Actions가 평일 미국 장 마감 후(06:15·06:45·07:30 KST 예약, 실제 시작은 보통 30~60분 늦음) 실행됩니다.

- `data/latest.json` — 최신 거래일의 SPY·VOO·SPYM·SSO·UPRO·SPXL·QQQ·QQQM·QLD·TQQQ 시가/고가/저가/종가, USD/KRW, 출처
- `data/fx_usdkrw.csv` — 원/달러 일별 환율(야후 KRW=X 종가)
- `data/daily/<TICKER>.csv` — 상장일부터 전체 일봉 (분할만 반영, 배당 미반영)

출처 순서: 야후(yfinance) → Stooq. 수동 실행: Actions 탭 → fetch-prices → Run workflow.
