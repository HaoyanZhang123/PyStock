from pathlib import Path

# 获取项目根路径
BASE_DIR = Path(__file__).resolve().parent

# 数据路径
DATA_PATH = BASE_DIR / 'data'
DB_PATH = DATA_PATH / 'stock_daily.sqlite'

# TuShare Token（从环境变量加载，fallback 到默认值）
import os
TUSHARE_TOKEN = os.getenv("TUSHARE_TOKEN", "your_token")  # 替换为实际 Token 或设置环境变量