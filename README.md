# 股票数据分析项目

## 写给所有看到这个项目的人
本人四个月前还是完全的电脑小白，靠着网上各种免费的教程、书籍、社区、ai、开源软件等学成现在的样子，这是我第一个从零动手自主开发、上传运营的项目。**发自内心的感谢所有愿意将知识免费分享出来的所有人，并且对所有自发维护这种开源氛围的人表达崇高的敬意**。<br>
我也会将这种精神继续传递下去，虽然我现在能做的东西（花了20+hours）浅显不够成熟，但是**我承诺,以后技术力不管如何，我永远会保持开源的态度，将自己会的一切知识无偿分享出来**。<br>

***知识属于所有愿意学习的人,知识与技术永远应该用于造福人类***。<br>
***Knowledge belongs to all who are willing to learn, and knowledge and technology should always be used to benefit humanity.***<br>
***在永无止境的学习中，与所有有缘看到此项目的人共勉。*** <br>
***In the endless pursuit of learning, I share this sentiment with all who happen to come across this project.***

## 注意事项
1.由于github以及git LFS限制，实际上的stock_daily.sqlite并未被上传，但是可以根据README的内容自行爬取。<br>
2.本项目最关键的模型回测和选股功能并未开发，由于技术力有限，本人打算结合手动测试，因此以后的版本也许也看不到这些功能，十分抱歉！<br>
3.本项目为了隐私保护，未上传实际token，请自行注册tushare以使用。<br>
4.项目中的config.py包含隐私信息，未上传，使用config_template.py代替，使用时将token替换成自己的即可。

## 项目概述
使用 TuShare 获取A股数据，进行分析和可视化。

## 目录结构
- data/: 存储数据文件
  - daily:啥都没有
  - stock_list.csv: A股列表（以“00”“60”开头的股票） 
  - stock_daily.sqlite:存了stock_list.csv里所有股票从2023.1.1至今的数据包括：
    股票代码（ts_code）：如 000001.SZ（平安银行）
    交易日期（trade_date）：格式为 YYYYMMDD，例如 20230101。
    开盘价（open）：每日开盘价格。<br>
    最高价（high）：每日最高价格。<br>
    最低价（low）：每日最低价格。<br>
    收盘价（close）：每日收盘价格。<br>
    前收盘价（pre_close）：前一交易日收盘价。<br>
    成交量（vol）：每日成交量（单位：股）。<br>
    成交额（amount）：每日成交额（单位：千元）。<br>
- JustForRead/：搭建的完整过程以及一些小tip，没什么特别大的参考价值，建议阅读下文的##环境配置+tip
- scripts/: Python 脚本
  - _pycache_:自动生成目录，主要用于存储编译后的 Python 字节码文件。
  - fetch_stock_list.py: 获取股票列表
  - fetch_daily_data.py: 批量下载日线数据
  - MU.py: 更新股票，以及更新数据
  - test_tushare.py:测试用
- venv/:虚拟环境
- .gitignore：不用上传到公共仓库的东西，保护隐私
- config_template.py:config.py的模板，没有实际内容
- config.py: API 密钥配置，以及路径配置
- README.md:整个项目的概览
- requirements.txt: 依赖列表

## 环境配置+tips
1. 激活虚拟环境：`source venv/Scripts/activate`(windows)
2. 安装依赖：`pip install -r requirements.txt`
3. 安装依赖：`D:\Python\python.exe -m pip install -r requirements.txt`  因为python出了点问题，命令行加上绝对路径
4. 配置 `config.py` 中的 TuShare Token，相关py的路径参考着前面完成的py来


## 运行
1. 测试数据接口: `python scripts/test_tushare.py` 
1. 获取股票列表：`python scripts/fetch_stock_list.py`
2. 批量下载日线数据：`python scripts/fetch_daily_data.py`
3. 更新增量数据：`python scripts/MU.py`
   输入："1": 检查并移除 ST 或退市股票
         "2": 更新每日股票数据
         "3": 退出

## 数据存储
- 股票列表存储在 `data/stock_list.csv`，包含 `ts_code`, `symbol`, `name`, `area`, `industry`。
- 日线数据存储在 `data/stock_daily.sqlite`，包含 `ts_code`（股票代码）, `trade_date`（交易日期）, `open`（开盘价）, `high`（最高价）, `low`（最低价）, `close`（收盘价）,`pre_close`（前一交易日收盘价）, `vol`（成交量）, `amount`（成交额）。
- 所有 CSV 文件和.sqlite使用 UTF-8 编码，防止中文乱码。
- 更新机制：检查最新日期，追加新数据。

## 注意事项
- TuShare API 有积分限制，批量下载时可能需要分批运行。
- 定期运行 `MU.py` 以保持数据最新。
- 不要将 `config.py` 提交到 Git（已包含在 `.gitignore` 中）。
- TuShare 的 API 有时对国际访问有限制，不要搭梯子会快很多。
- 如果在“输出”中中文乱码，在该py中加入
  import sys<br>
  import io<br>
  sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')<br>
- 如果日志乱码，右下角UTF-8，“通过编码重新打开”，“中文”
