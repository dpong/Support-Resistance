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


style.use('ggplot')

def supres(low, high, n=21, min_touches=2, stat_likeness_percent=2, bounce_percent=5):
    # Collapse into dataframe
    df = pd.concat([high, low], keys = ['high', 'low'], axis=1)
    df['sup'] = pd.Series(np.zeros(len(low)))
    df['res'] = pd.Series(np.zeros(len(low)))
    df['sup_break'] = pd.Series(np.zeros(len(low)))
    df['sup_break'] = 0
    df['res_break'] = pd.Series(np.zeros(len(high)))
    df['res_break'] = 0
    
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
    ret_df = pd.concat([df['sup'], df['res'], df['sup_break'], df['res_break']], keys = ['sup', 'res', 'sup_break', 'res_break'], axis=1)
    return ret_df

startTime = '2018-1-01'
df = pdr.DataReader('^TWII','yahoo', startTime,)

ret_df = supres(df['High'],df['Low'])
for column in ret_df.columns:
    df[column] = ret_df[column]

last_sup = df[(~np.isnan(df['sup']))]['sup'][-1]
last_sup_date=df[(~np.isnan(df['sup']))].index[-1]
last_res = df[(~np.isnan(df['res']))]['res'][-1]
last_res_date=df[(~np.isnan(df['res']))].index[-1]
daydelta = last_res_date - last_sup_date

if last_res > last_sup:
    df['Close'][-42:].plot()
    plt.axhline(last_sup,color='g',label='Support')
    plt.axhline(last_res,color='b',label='Resistance')
else:
    if daydelta.days > 0:       #跌破支撐後有壓力
        df['Close'][-42:].plot()
        plt.axhline(last_res,color='b',label='Resistance')
    elif daydelta.days < 0:     #突破後有支撐
        df['Close'][-42:].plot()
        plt.axhline(last_sup,color='g',label='Support')
plt.legend()        
    





