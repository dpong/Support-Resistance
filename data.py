import json,requests
import pandas as pd
import datetime

def get_crypto_from_api(ticker, data_quantity, frequency):
    api_key = '892a9ae426638c8a4214b3c0d85fe95de0f883dee89db4948d1694ae01be7fbe'
    url = 'https://min-api.cryptocompare.com/data/histo{}?fsym={}&tsym=USD&limit={}&api_key={}'.format(frequency, ticker, data_quantity, api_key)
    response = requests.get(url)
    dataset = response.json()
    df =pd.DataFrame(dataset['Data'])
    # 時間轉換
    df['Date'] = '0'
    for i in range(data_quantity+1):
        df.at[i,'Date'] = str(datetime.datetime.fromtimestamp(df.at[i,'time']))
    # 成交量計算
    df['Volume'] = df['volumeto'] - df['volumefrom']
    df.drop(columns={'volumefrom','volumeto','time'},inplace=True)
    df.rename(columns={'close':"Close", 'open':"Open", 'high':'High', 'low':"Low"}, inplace=True)
    return df

def df_to_csv(df, ticker, data_quantity, frequency):
    df.to_csv('data/{}_{}_{}_data.csv'.format(frequency,ticker,data_quantity))


if __name__=='__main__':
    frequency = 'day'  # day, minute, hour
    ticker = 'ETH'
    data_quantity = 400
    df = get_crypto_from_api(ticker, data_quantity, frequency)
    #df_to_csv(df, ticker, data_quantity, frequency)