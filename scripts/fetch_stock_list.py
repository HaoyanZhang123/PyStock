# scripts/fetch_stock_list.py
import tushare as ts
import pandas as pd
from config import DATA_PATH, TUSHARE_TOKEN
from pathlib import Path

# 初始化 TuShare
ts.set_token(TUSHARE_TOKEN)
pro = ts.pro_api()

# 设置输出文件路径
output_file = DATA_PATH / 'stock_list.csv'

# 确保 data 目录存在
DATA_PATH.mkdir(parents=True, exist_ok=True)

if output_file.exists():
    print(f"{output_file} 已存在，跳过获取股票列表")
else:
    # 获取股票列表，仅保留以“00”或“60”开头的股票
    stock_list = pro.stock_basic(exchange='', list_status='L', fields='ts_code,symbol,name,area,industry')
    stock_list = stock_list[stock_list['ts_code'].str.startswith(('00', '60'))]
    stock_list.to_csv(output_file, index=False, encoding='utf-8')
    print(f"股票列表已保存至 {output_file}")
