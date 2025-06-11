import tushare as ts
import pandas as pd
import sqlite3
import time
from pathlib import Path
from config import DATA_PATH, DB_PATH, TUSHARE_TOKEN

# 初始化 TuShare
try:
    ts.set_token(TUSHARE_TOKEN)
    pro = ts.pro_api()
except Exception as e:
    print(f"初始化失败: {e}")
    exit(1)

# 读取股票列表
stock_list_file = DATA_PATH / 'stock_list.csv'
stock_list = pd.read_csv(stock_list_file, encoding='utf-8')
total_stocks = len(stock_list)

# 建立 SQLite 连接
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# 创建表（如不存在）
cursor.execute('''
CREATE TABLE IF NOT EXISTS daily (
    ts_code TEXT,
    trade_date TEXT,
    open REAL,
    high REAL,
    low REAL,
    close REAL,
    pre_close REAL,
    vol REAL,
    amount REAL,
    PRIMARY KEY (ts_code, trade_date)
)
''')
conn.commit()

# 控速设置：每分钟最多 400 次请求
requests_per_minute = 400
sleep_interval = 60.0 / requests_per_minute

# 遍历股票列表并写入 SQLite
for idx, ts_code in enumerate(stock_list['ts_code']):
    progress = (idx + 1) / total_stocks * 100
    print(f"处理进度: [{idx + 1}/{total_stocks}] {progress:.1f}% - 当前股票: {ts_code}", end='\r')

    try:
        # 如果该股票已存在数据，跳过
        cursor.execute("SELECT COUNT(*) FROM daily WHERE ts_code = ?", (ts_code,))
        count = cursor.fetchone()[0]

        if count == 0:
            df = pro.daily(
                ts_code=ts_code,
                start_date='20230101',
                end_date='20250610',
                fields='ts_code,trade_date,open,high,low,close,pre_close,vol,amount'
            )
            if not df.empty:
                df.to_sql('daily', conn, if_exists='append', index=False)
                print(f"处理进度: [{idx + 1}/{total_stocks}] {progress:.1f}% - {ts_code} 数据已写入 SQLite", end='\r')
            else:
                print(f"处理进度: [{idx + 1}/{total_stocks}] {progress:.1f}% - {ts_code} 无数据", end='\r')
        else:
            print(f"处理进度: [{idx + 1}/{total_stocks}] {progress:.1f}% - {ts_code} 已存在于数据库中，跳过", end='\r')
    except Exception as e:
        print(f"处理进度: [{idx + 1}/{total_stocks}] {progress:.1f}% - {ts_code} 下载失败: {e}", end='\r')

    time.sleep(sleep_interval)

# 关闭连接
conn.close()
print("\n所有数据已写入 SQLite。")
