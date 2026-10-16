import sqlite3
import json
from datetime import datetime, timezone
import pytz

kst = pytz.timezone('Asia/Seoul')
start_time = datetime.now(timezone.utc)
start_time_kst = start_time.astimezone(kst)
start_time_str = start_time_kst.strftime('%Y-%m-%d %H:%M:%S KST')
today = start_time_kst.strftime('%Y-%m-%d')
print(f'작업 시작: {start_time_str} | 날짜: {today}')

# 수집된 지표값 (WebSearch 결과 기준, 2026-10-16)
sp500       = 7744.06    # Oct 15 close (US market not open yet at 13:14 UTC)
nasdaq      = 26713.03   # Oct 15 close
dow_jones   = 52177.69   # Oct 15 close
kospi       = 5668.05    # Oct 16 confirmed close (KST)
kosdaq      = 794.78     # Oct 16 confirmed close (KST)
nikkei      = 65598.63   # Oct 16 intraday as of 10:02 AM JST
shanghai    = 3813.79    # Oct 16 (Bloomberg-syndicated source)
wti_oil     = 97.39      # Oct 16 live quote USD/barrel
brent_oil   = 105.45     # Oct 16 live quote USD/barrel
gold        = 4177.40    # Oct 16 spot USD/troy oz
copper      = 6.61       # Oct 14 close USD/pound (most recent confirmed)
dxy         = 101.729    # Oct 16
usd_krw     = 1331.4     # Oct 16 KRW/USD
usd_jpy     = 158.05     # Oct 16
eur_usd     = 1.1224     # Oct 16
us_10y_yield = 5.061     # Oct 15 close (%) - most recent before US open Oct 16
vix         = 16.87      # Oct 14 close (most recent available)
us_cpi      = 3.7        # September 2026 YoY (%)
fed_rate    = 3.88       # Effective fed funds rate, target range 3.75-4.00%
china_pmi   = 50.1       # September 2026 (NBS official)

# SQLite DB 저장
conn = sqlite3.connect('/home/user/world-indicators/claude/world_indicators.db')
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS world_indicators (
    date        TEXT PRIMARY KEY,
    sp500       REAL, nasdaq      REAL, dow_jones   REAL,
    kospi       REAL, kosdaq      REAL, nikkei      REAL, shanghai    REAL,
    wti_oil     REAL, brent_oil   REAL, gold        REAL, copper      REAL,
    dxy         REAL, usd_krw     REAL, usd_jpy     REAL, eur_usd     REAL,
    us_10y_yield REAL, vix        REAL,
    us_cpi      REAL, fed_rate    REAL, china_pmi   REAL,
    collected_at TEXT,
    updated_at  TEXT
)
''')

now_str = datetime.now(timezone.utc).astimezone(kst).strftime('%Y-%m-%d %H:%M:%S KST')

cursor.execute('''
INSERT OR REPLACE INTO world_indicators
    (date, sp500, nasdaq, dow_jones, kospi, kosdaq, nikkei, shanghai,
     wti_oil, brent_oil, gold, copper,
     dxy, usd_krw, usd_jpy, eur_usd,
     us_10y_yield, vix, us_cpi, fed_rate, china_pmi,
     collected_at, updated_at)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
''', (
    today,
    sp500, nasdaq, dow_jones, kospi, kosdaq, nikkei, shanghai,
    wti_oil, brent_oil, gold, copper,
    dxy, usd_krw, usd_jpy, eur_usd,
    us_10y_yield, vix, us_cpi, fed_rate, china_pmi,
    start_time_str, now_str
))

conn.commit()
conn.close()
print(f'DB 저장 완료: {today}')

# 로그 파일 저장
end_time = datetime.now(timezone.utc)
end_time_kst = end_time.astimezone(kst)
end_time_str = end_time_kst.strftime('%Y-%m-%d %H:%M:%S KST')
duration_sec = int((end_time - start_time).total_seconds())

log = {
    'date': today,
    'start_time': start_time_str,
    'end_time': end_time_str,
    'duration_seconds': duration_sec,
    'collected': {
        'sp500': sp500, 'nasdaq': nasdaq, 'dow_jones': dow_jones,
        'kospi': kospi, 'kosdaq': kosdaq, 'nikkei': nikkei, 'shanghai': shanghai,
        'wti_oil': wti_oil, 'brent_oil': brent_oil, 'gold': gold, 'copper': copper,
        'dxy': dxy, 'usd_krw': usd_krw, 'usd_jpy': usd_jpy, 'eur_usd': eur_usd,
        'us_10y_yield': us_10y_yield, 'vix': vix,
        'us_cpi': us_cpi, 'fed_rate': fed_rate, 'china_pmi': china_pmi
    },
    'none_count': sum(1 for v in [sp500, nasdaq, dow_jones, kospi, kosdaq, nikkei, shanghai,
        wti_oil, brent_oil, gold, copper, dxy, usd_krw, usd_jpy, eur_usd,
        us_10y_yield, vix, us_cpi, fed_rate, china_pmi] if v is None)
}

log_path = f'/home/user/world-indicators/claude/logs/log_{today}.json'
with open(log_path, 'w', encoding='utf-8') as f:
    json.dump(log, f, ensure_ascii=False, indent=2)

print(f'로그 저장: {log_path}')
print(f'시작: {start_time_str} | 종료: {end_time_str} | 소요: {duration_sec}초')
print(f'수집 항목 수: {20 - log["none_count"]}/20 (None: {log["none_count"]})')
