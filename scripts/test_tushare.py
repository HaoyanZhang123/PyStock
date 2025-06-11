# scripts/test_tushare.py
import tushare as ts
from config import TUSHARE_TOKEN

ts.set_token(TUSHARE_TOKEN)
pro = ts.pro_api()
df = pro.daily(ts_code="000001.SZ", start_date="20230101", end_date="20230201")
print(df.head())