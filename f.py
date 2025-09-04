import requests
import pandas as pd
import matplotlib.pyplot as plt
from lxml import html

# ----------------------------
# 1️⃣ 設定股票代號與參數
# ----------------------------
ticker = '1231'
Rf = 0.015   # 無風險利率 (10年公債)
Rm = 0.08    # 市場報酬率

# ----------------------------
# 2️⃣ 抓取 Beta (5年)
# ----------------------------
beta_url = f"https://goodinfo.tw/tw/StockDetail.asp?STOCK_ID={ticker}"
resp = requests.get(beta_url)
tree = html.fromstring(resp.text)
beta_str = tree.xpath('//*[@id="secKLine"]/section[1]/table/tbody/tr[2]/td[8]/a/text()')
beta = float(beta_str[0]) if beta_str else 1.0
Ke = Rf + beta * (Rm - Rf)
print(f"Beta (5年): {beta}, Ke: {Ke:.4f}")

# ----------------------------
# 3️⃣ 抓取歷年財報表格
# Goodinfo 綜合損益表、資產負債表 (範例抓合併年報)
# ----------------------------
income_url = f"https://goodinfo.tw/tw/StockFinancialStatement.asp?STOCK_ID={ticker}&RPT_CAT=BS_M_YEAR"
tables = pd.read_html(income_url)

# 假設第0個 table 是綜合損益表，第1個是資產負債表
income_df = tables[0]
balance_df = tables[1]

# 這裡需要根據實際表格欄位整理，取出以下欄位：
# Year, Revenue(營收), Gross_Profit(毛利), Income_Before_Tax(稅前淨利),
# Income_Tax(所得稅), Equity(股東權益), Short_Term_Debt(短期借款), Long_Term_Debt(長期借款),
# Interest_Expense(利息費用)
# 假設已整理成 df
df = pd.DataFrame({
    'Year': [2022, 2021, 2020, 2019, 2018],
    'Revenue': [70000000, 65000000, 60000000, 58000000, 54000000],
    'Gross_Profit': [15000000, 14000000, 13000000, 12500000, 12000000],
    'Income_Before_Tax': [3000000, 3500000, 2800000, 2500000, 2200000],
    'Income_Tax': [600000, 700000, 560000, 500000, 440000],
    'Equity': [20000000, 18000000, 17000000, 16000000, 15000000],
    'Short_Term_Debt': [5000000, 4000000, 3500000, 3000000, 2500000],
    'Long_Term_Debt': [7000000, 6500000, 6000000, 5800000, 5500000],
    'Interest_Expense': [300000, 280000, 250000, 240000, 220000]
})

# ----------------------------
# 4️⃣ 計算指標
# ----------------------------
df['Gross_Margin'] = df['Gross_Profit'] / df['Revenue']
df['Debt'] = df['Short_Term_Debt'] + df['Long_Term_Debt']
df['Tax_Rate'] = df['Income_Tax'] / df['Income_Before_Tax']
df['Kd'] = df['Interest_Expense'] / df['Debt']
df['WACC'] = (df['Equity']/(df['Equity']+df['Debt']))*Ke + \
             (df['Debt']/(df['Equity']+df['Debt']))*df['Kd']*(1-df['Tax_Rate'])
df['NOPAT'] = df['Income_Before_Tax'] * (1 - df['Tax_Rate'])
df['ROIC'] = df['NOPAT'] / (df['Equity'] + df['Debt'])

# ----------------------------
# 5️⃣ 畫圖
# ----------------------------
plt.figure(figsize=(12,6))
plt.plot(df['Year'], df['ROIC'], marker='o', label='ROIC')
plt.plot(df['Year'], df['WACC'], marker='s', label='WACC')
plt.plot(df['Year'], df['Gross_Margin'], marker='^', label='毛利率')
plt.xlabel('Year')
plt.ylabel('比率')
plt.title(f'{ticker} 歷年 ROIC / WACC / 毛利率')
plt.grid(True)
plt.legend()
plt.show()
