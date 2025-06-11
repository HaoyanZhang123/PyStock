import tushare as ts
import pandas as pd
import sqlite3
import time
import logging
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from datetime import datetime
from config import DATA_PATH, DB_PATH, TUSHARE_TOKEN


# 配置日志
logging.basicConfig(level=logging.INFO, filename='update.log', filemode='a', format='%(asctime)s - %(message)s',encoding='utf-8')
logger = logging.getLogger(__name__)

# 初始化 TuShare
try:
    ts.set_token(TUSHARE_TOKEN)
    pro = ts.pro_api()
except Exception as e:
    logger.error(f"初始化失败: {e}")
    exit(1)

# 读取股票列表
stock_list_file = DATA_PATH / 'stock_list.csv'
if not stock_list_file.exists():
    logger.error(f"文件 {stock_list_file} 不存在，请先运行生成 stock_list.csv 的脚本。")
    exit(1)
stock_list = pd.read_csv(stock_list_file, encoding='utf-8')
total_stocks = len(stock_list)  # 总股票数量

# 建立 SQLite 连接
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# 创建表并添加索引
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
cursor.execute('CREATE INDEX IF NOT EXISTS idx_ts_code_date ON daily (ts_code, trade_date)')
conn.commit()

# 获取当前日期
current_date = datetime.now().strftime('%Y%m%d')

def check_and_remove_st_delisted():
    global stock_list  # 声明全局变量
    logger.info("开始检查 ST 或退市股票...")
    updated_stocks = 0

    for idx, row in enumerate(stock_list.itertuples()):
        ts_code = row.ts_code
        progress = (idx + 1) / total_stocks * 100
        print(f"检查进度: [{idx + 1}/{total_stocks}] {progress:.1f}% - 当前股票: {ts_code}", end='\r')

        try:
            # 获取最新股票状态
            stock_info = pro.stock_basic(ts_code=ts_code, fields='ts_code,list_status')
            if stock_info['list_status'].iloc[0] in ['D', 'P']:  # D: 退市, P: 暂停上市
                # 从 stock_list.csv 删除
                stock_list = stock_list[stock_list['ts_code'] != ts_code]
                # 从 SQLite 删除
                cursor.execute("DELETE FROM daily WHERE ts_code = ?", (ts_code,))
                conn.commit()
                updated_stocks += 1
                print(f"检查进度: [{idx + 1}/{total_stocks}] {progress:.1f}% - {ts_code} (ST/退市) 已移除", end='\r')
            else:
                print(f"检查进度: [{idx + 1}/{total_stocks}] {progress:.1f}% - {ts_code} 正常", end='\r')
        except Exception as e:
            print(f"检查进度: [{idx + 1}/{total_stocks}] {progress:.1f}% - {ts_code} 检查失败: {e}", end='\r')
            with open('failures.log', 'a', encoding='utf-8') as f:
                f.write(f"{ts_code}: {e}\n")

        time.sleep(0.15)  # 控制速率

    # 保存更新后的 stock_list.csv
    stock_list.to_csv(stock_list_file, index=False, encoding='utf-8')
    logger.info(f"完成检查，共移除 {updated_stocks} 只 ST/退市股票。")
    print(f"\n完成检查，共移除 {updated_stocks} 只 ST/退市股票。")

def update_daily_data():
    logger.info("开始更新每日数据...")
    total_stocks = len(stock_list)
    updated_stocks = 0

    for idx, ts_code in enumerate(stock_list['ts_code']):
        progress = (idx + 1) / total_stocks * 100
        print(f"更新进度: [{idx + 1}/{total_stocks}] {progress:.1f}% - 当前股票: {ts_code}", end='\r')

        try:
            # 查询数据库最新日期
            cursor.execute("SELECT MAX(trade_date) FROM daily WHERE ts_code = ?", (ts_code,))
            last_date = cursor.fetchone()[0]
            # 使用 bdate_range 检查交易日
            start_date = current_date if not last_date else pd.bdate_range(
                end=current_date,
                start=(pd.to_datetime(last_date) + pd.Timedelta(days=1)).strftime('%Y%m%d'),
                freq='B'
            )[-1].strftime('%Y%m%d')

            if pd.to_datetime(start_date) <= pd.to_datetime(current_date):
                df = pro.daily(
                    ts_code=ts_code,
                    start_date=start_date,
                    end_date=current_date,
                    fields='ts_code,trade_date,open,high,low,close,pre_close,vol,amount'
                )
                if not df.empty:
                    # 转换 trade_date 格式
                    df['trade_date'] = pd.to_datetime(df['trade_date']).dt.strftime('%Y%m%d')
                    # 使用事务模式优化插入
                    with conn:
                        df.to_sql('daily', conn, if_exists='append', index=False, method='multi')
                    updated_stocks += 1
                    print(f"更新进度: [{idx + 1}/{total_stocks}] {progress:.1f}% - {ts_code} 数据已更新", end='\r')
                else:
                    print(f"更新进度: [{idx + 1}/{total_stocks}] {progress:.1f}% - {ts_code} 无新数据", end='\r')
            else:
                print(f"更新进度: [{idx + 1}/{total_stocks}] {progress:.1f}% - {ts_code} 已最新", end='\r')
        except Exception as e:
            print(f"更新进度: [{idx + 1}/{total_stocks}] {progress:.1f}% - {ts_code} 更新失败: {e}", end='\r')
            with open('failures.log', 'a', encoding='utf-8') as f:
                f.write(f"{ts_code}: {e}\n")

        time.sleep(0.15)  # 控制速率

    logger.info(f"完成更新，共更新 {updated_stocks} 只股票数据。")
    print(f"\n完成更新，共更新 {updated_stocks} 只股票数据。")

# 主程序
while True:
    print("\n请选择功能:")
    print("1. 检查并移除 ST 或退市股票")
    print("2. 更新每日股票数据")
    print("3. 退出")
    choice = input("请输入选项 (1-3): ")

    if choice == '1':
        check_and_remove_st_delisted()
    elif choice == '2':
        update_daily_data()
    elif choice == '3':
        break
    else:
        print("无效选项，请重新输入。")

# 关闭连接
conn.close()
logger.info("程序结束。")
print("程序结束。")