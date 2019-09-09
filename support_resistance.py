#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 22 22:50:26 2019

@author: dpong
"""
import pandas as pd
import numpy as np
import pandas_datareader as pdr
import matplotlib.pyplot as plt
from matplotlib import style
from mpl_finance import candlestick_ohlc
from data import *



def identify(openp, high, low, close, n=21, min_touches=2, stat_likeness_percent=2,bounce_percent=5):
    # Collapse into dataframe
    df = pd.concat([openp, high, low, close], keys = ['open', 'high', 'low','close'], axis=1)
    df.loc[:,'sup'] = pd.Series(np.zeros(len(low)))
    df.loc[:,'res'] = pd.Series(np.zeros(len(high)))
    df.loc[:,'sup_break'] = pd.Series(np.zeros(len(low)))
    df.loc[:,'res_break'] = pd.Series(np.zeros(len(high)))
    for x in range((n-1)+n, len(df)):
        # Split into defined timeframes for analysis
        tempdf = df[x-n:x+1]
        # Setting default values for support and resistance to None
        sup = None
        res = None
        # Identifying local high and local low
        maxima = tempdf.high.max()
        minima = tempdf.low.min()
        # Calculating distance between max and min (total price movement)
        move_range = maxima - minima
        # Calculating bounce distance and allowable margin of error for likeness
        move_allowance = move_range * (stat_likeness_percent / 100)
        bounce_distance = move_range * (bounce_percent / 100)
        # Test resistance by iterating through data to check for touches delimited by bounces
        touchdown = 0
        awaiting_bounce = False
        for y in range(0, len(tempdf)):
            if abs(maxima - tempdf.high.iloc[y]) < move_allowance and not awaiting_bounce:
                touchdown = touchdown + 1
                awaiting_bounce = True
            elif abs(maxima - tempdf.high.iloc[y]) > bounce_distance:
                awaiting_bounce = False
        if touchdown >= min_touches:
            res = maxima
            touchdown = 0
        awaiting_bounce = False
        for y in range(0, len(tempdf)):
            if abs(tempdf.low.iloc[y] - minima) < move_allowance and not awaiting_bounce:
                touchdown = touchdown + 1
                awaiting_bounce = True
            elif abs(tempdf.low.iloc[y] - minima) > bounce_distance:
                awaiting_bounce = False
        if touchdown >= min_touches:
            sup = minima
        if sup:
            df.iloc[x,df.columns.get_loc('sup')]=sup   #修改自df['sup'].iloc[x] = sup 
        if res:
            df.iloc[x,df.columns.get_loc('res')]=res   #修改自df['res'].iloc[x] = res 
    res_break_indices = list(df[(np.isnan(df['res']) & ~np.isnan(df.shift(1)['res'])) & (df['high'] > df.shift(1)['res'])].index)
    for index in res_break_indices:
        df['res_break'].at[index] = 1
    sup_break_indices = list(df[(np.isnan(df['sup']) & ~np.isnan(df.shift(1)['sup'])) & (df['low'] < df.shift(1)['sup'])].index) 
    for index in sup_break_indices:
        df['sup_break'].at[index] = 1
    ret_df = pd.concat([df['open'], df['high'], df['low'], df['close'], df['sup'], df['res'], df['sup_break'], df['res_break']],
                       keys = ['open', 'high', 'low', 'close','sup', 'res', 'sup_break', 'res_break'], axis=1)
        #整理
    res_list = ret_df[(~np.isnan(ret_df['res']))]['res']
    sup_list = ret_df[(~np.isnan(ret_df['sup']))]['sup']
        
    return ret_df, res_list, sup_list
    
def drawing(ret_df):
        #處理
    last_sup = ret_df['sup']
    last_sup = last_sup.iloc[last_sup.nonzero()].iloc[-1]
    last_res = ret_df['res']
    last_res = last_res.iloc[last_res.nonzero()].iloc[-1]
    #daydelta = last_res_date - last_sup_date
        #判斷
    if last_res > last_sup:
        ret_df['close'][-100:].plot()
        plt.axhline(last_sup,color='g',label='Support')
        plt.axhline(last_res,color='b',label='Resistance')
    else:
        if daydelta.days > 0:       #跌破支撐後有壓力
            ret_df['close'][-42:].plot()
            plt.axhline(last_res,color='b',label='Resistance')
        elif daydelta.days < 0:     #突破後有支撐
            ret_df['close'][-42:].plot()
            plt.axhline(last_sup,color='g',label='Support')
    plt.legend()
    plt.ylabel('Price')        
    plt.show()
    
   

if __name__=='__main__':
    frequency = 'day'
    ticker = 'BTC'
    data_quantity = 400
    df = get_crypto_from_api(ticker, data_quantity, frequency)
    ret_df, res_list, sup_list = identify(df['Open'], df['High'], df['Low'], df['Close'],)
    drawing(ret_df)












