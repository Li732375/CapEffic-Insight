import requests
from lxml import html
import re
from datetime import datetime


STOCK_CODE = "2330"  # 台股股票代號
TARGET_KEYS = ["現金及約當現金", "1100"]  # 目標會計代號或名稱

def extract_chinese(text):
    # 保留中文，排除英文、空格或其他符號
    match = re.match(r'([\u4e00-\u9fff]+)', text)
    return match.group(1) if match else text.strip()

def fetch_html_with_IFRSs_after(year, stock_code, season, table_index):
    '''
    table_index:
    資產負債表:1
    綜合損益表:2
    現金流量表:3
    '''
    url = f"https://mopsov.twse.com.tw/server-java/t164sb01?step=3&SYEAR={year}&file_name=tifrs-fr1-m1-ci-cr-{stock_code}-{year}Q{season}.html"
    res = requests.get(url)
    if res.status_code != 200:
        print(f"網站資料請求失敗或該資料尚不存在，狀態碼：{res.status_code}")
        return None
    
    res.encoding = "big5-hkscs"
    tree = html.fromstring(res.text)
    table = tree.xpath('//div[@class="container"]/div[@class="content"]/table[1]')[table_index]

    # 建立代號與名稱字典，兩者指向的值相同
    data = {}

    # 解析表格內容
    for tr in table.xpath('.//tr'):
        cells = [td.text_content().strip() for td in tr.xpath('./td')]
        if cells and len(cells) > 2:
            # 第一欄若沒代號則跳過
            if not cells[0]:
                continue
            
            # 第二欄保留中文
            name = extract_chinese(cells[1])
            
            # 第三欄去掉逗號轉整數
            value_str = cells[2].replace(',', '').replace('(', '-').replace(')', '')
            try:
                value = int(value_str)
            except ValueError:
                value = None
            
            code = cells[0]
            
            # 如果是目標代號或名稱才收集
            if code in TARGET_KEYS or name in TARGET_KEYS:
                data[code] = value
                data[name] = value

    return data

if __name__ == "__main__":
    current_year = datetime.now().year
    # 建立歷年資料字典
    historical_data = {key: [] for key in TARGET_KEYS}

    # 抓取 IFRSs 前(民國101年(2012)(含)的資料)

    # 抓取 IFRSs 後(民國102年(2013)到目前的資料)
    for year in range(102 + 1911, current_year):
        for season in [1, 2, 3, 4]:
            for type in [1, 2, 3]:
                data = fetch_html_with_IFRSs_after(year, 
                                                   STOCK_CODE, 
                                                   season, 
                                                   type)
                
                # 依序填入資料
                if data:
                    for key in TARGET_KEYS:
                        historical_data[key].append(data[key])
                else:
                    # 抓取失敗時，用 None 填補
                    for key in TARGET_KEYS:
                        historical_data[key].append(None)
        