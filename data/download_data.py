import ccxt
import pandas as pd
from datetime import datetime, timedelta, timezone
import time

# 1) 连接交易所（Binance）
exchange = ccxt.binance({
    'enableRateLimit': True,
})

symbol = 'ETH/USDT'
timeframe = '5m'
limit = 1000  # 单次最多取1000根（常见设置）
since_dt = datetime.now(timezone.utc) - timedelta(days=800)
since_ms = int(since_dt.timestamp() * 1000)

all_ohlcv = []

while True:
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe=timeframe, since=since_ms, limit=limit)
    if not ohlcv:
        break

    all_ohlcv.extend(ohlcv)

    # 下一次从最后一根K线之后开始
    last_ts = ohlcv[-1][0]
    next_since = last_ts + 5 * 60 * 1000  # 5分钟
    if next_since <= since_ms:
        break
    since_ms = next_since

    # 如果已经接近当前时间，可退出
    if last_ts >= exchange.milliseconds() - 5 * 60 * 1000:
        break

    time.sleep(exchange.rateLimit / 1000)

# 去重并转DataFrame
df = pd.DataFrame(all_ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
df = df.drop_duplicates(subset=['timestamp']).sort_values('timestamp').reset_index(drop=True)
df['datetime'] = pd.to_datetime(df['timestamp'], unit='ms', utc=True)

# 调整列顺序
df = df[['datetime', 'open', 'high', 'low', 'close', 'volume']]

print(df.head())
print(df.tail())
print(f'总条数: {len(df)}')

# 可选：保存
df.to_csv('eth_usdt_5m_2y.csv', index=False)
