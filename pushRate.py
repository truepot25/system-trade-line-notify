
import sys
from yahoo_finance_api2 import share
from yahoo_finance_api2.exceptions import YahooFinanceError
import pandas as pd
import datetime
import requests

def main():
    # 始値を取得
    open_stock_rate = get_open_stock('8783')
    current_stock_rate = get_current_stock('8783')
    if pd.isna(current_stock_rate):
        return

    message = culc_profit_and_loss_ratio(open_stock_rate, current_stock_rate, 4)
    if message != "":
        token = get_token()
        send_line_notify(message, token)

# 指定の日本株証券コードで株価を取得し始値を返す
def get_open_stock(code):
    my_share = share.Share(f'{code}.T')
    symbol_data = None

    try:
        symbol_data = my_share.get_historical(
            share.PERIOD_TYPE_DAY, 1,
            share.FREQUENCY_TYPE_DAY, 1)
    except YahooFinanceError as e:
        print(e.message)
        sys.exit(1)

    open = symbol_data["open"]
    return open[0]

# 指定の日本株証券コードで株価を取得
def get_current_stock(code):
    my_share = share.Share(f'{code}.T')
    symbol_data = None

    try:
        symbol_data = my_share.get_historical(
            share.PERIOD_TYPE_DAY, 1,
            share.FREQUENCY_TYPE_MINUTE, 1)
    except YahooFinanceError as e:
        print(e.message)
        sys.exit(1)
 
    # df = pd.DataFrame(symbol_data)
    #日本時間へ変換
    # df["datetime_JST"] = pd.to_datetime(df.timestamp, unit="ms") + datetime.timedelta(hours=9)
    # return df.head()   
    high = symbol_data["high"]
    return high[len(high) - 1]

# line_notifyのトークンをtoken.txtの1行目から取得する
def get_token():
    with open('./token.txt') as f:
        token = f.readline().rstrip()
    return token

# 始値が現在値から指定するだけ低くなればTrueを返す
def culc_profit_and_loss_ratio(base_num, current_num, ratio):
    profit_and_loss_ratio = current_num / base_num * 100
    if profit_and_loss_ratio <= 100 - ratio :
        return generate_message(base_num, current_num, format(abs(100 - profit_and_loss_ratio), '.2f'), "↘︎")
    elif profit_and_loss_ratio >= 100 + ratio :
        return generate_message(base_num, current_num, format(abs(100 - profit_and_loss_ratio), '.2f'), "↗︎")
    else :
        return ""

# Lineに送るメッセージを生成する
def generate_message(open_stock_rate, current_stock_rate, ratio, str):
    dt_now = datetime.datetime.now()
    dt_now = dt_now.strftime('%Y年%m月%d日 %H:%M:%S')
    return f'\n☆{dt_now}\n\u0020始値：{open_stock_rate}\n\u0020現在：{current_stock_rate}（{ratio}%{str}）'

# line notifyで通知を送信
def send_line_notify(notification_message, line_notify_token):
    line_notify_api = 'https://notify-api.line.me/api/notify'
    headers = {'Authorization': f'Bearer {line_notify_token}'}
    data = {'message': notification_message}
    requests.post(line_notify_api, headers = headers, data = data)

# 直接実行のみ許可
if __name__ == "__main__":
    main()