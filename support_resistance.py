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
from data import *
import datetime, time, os



def identify(df, n=21, min_touches=2, stat_likeness_percent=2,bounce_percent=5):
    # Collapse into dataframe
    df['sup'] = np.nan
    df['res'] = np.nan
    for x in range((n-1)+n, len(df)):
        # Split into defined timeframes for analysis
        tempdf = df[x-n:x+1]
        # Setting default values for support and resistance to None
        sup = None
        res = None
        # Identifying local high and local low
        maxima = tempdf.High.max()
        minima = tempdf.Low.min()
        # Calculating distance between max and min (total price movement)
        move_range = maxima - minima
        # Calculating bounce distance and allowable margin of error for likeness
        move_allowance = move_range * (stat_likeness_percent / 100)
        bounce_distance = move_range * (bounce_percent / 100)
        # Test resistance by iterating through data to check for touches delimited by bounces
        touchdown = 0
        awaiting_bounce = False
        for y in range(0, len(tempdf)):
            if abs(maxima - tempdf.High.iloc[y]) < move_allowance and not awaiting_bounce:
                touchdown = touchdown + 1
                awaiting_bounce = True
            elif abs(maxima - tempdf.High.iloc[y]) > bounce_distance:
                awaiting_bounce = False
        if touchdown >= min_touches:
            res = maxima
            touchdown = 0
        awaiting_bounce = False
        for y in range(0, len(tempdf)):
            if abs(tempdf.Low.iloc[y] - minima) < move_allowance and not awaiting_bounce:
                touchdown = touchdown + 1
                awaiting_bounce = True
            elif abs(tempdf.Low.iloc[y] - minima) > bounce_distance:
                awaiting_bounce = False
        if touchdown >= min_touches:
            sup = minima
        if sup:
            df.iloc[x,df.columns.get_loc('sup')]=sup   #修改自df['sup'].iloc[x] = sup 
        if res:
            df.iloc[x,df.columns.get_loc('res')]=res   #修改自df['res'].iloc[x] = res 
    
    return df
    
def drawing(freq_type, ret_df, data_quantity):
    # 處理
    sup = ret_df['sup']
    sup_ = sup.dropna()
    last_sup = sup_.iloc[-1]
    res = ret_df['res']
    res_ = res.dropna()
    last_res = res_.iloc[-1]
    # open new folder
    new_date = time.strftime("%Y-%m-%d", time.localtime())
    newpath = r'D:\Dpong\Record\Res_Sup\{}'.format(new_date) 
    if not os.path.exists(newpath):
        os.makedirs(newpath)
    # plot
    style.use('ggplot')
    fig = plt.figure()
    ax1 = fig.add_subplot(1,1,1)
    ax1.plot(ret_df['Close'])
    ax1.axhline(last_sup ,color='g' ,label='Support')
    ax1.axhline(last_res ,color='b' ,label='Resistance')
    if freq_type == 'day':
        now_time = str(time.strftime("%Y-%m-%d", time.localtime()))
        plt.title('From: '+ now_time + ' backward {} {}s'.format(data_quantity, freq_type))
    elif freq_type == 'hour':
        now_time = str(time.strftime("%Y-%m-%d %H", time.localtime()))
        plt.title('From: '+ now_time + ' backward {} {}s'.format(data_quantity, freq_type))
    elif freq_type == 'minute':
        now_time = str(time.strftime("%Y-%m-%d %H:%M", time.localtime()))
        plt.title('From: '+ now_time + ' backward {} {}s'.format(data_quantity, freq_type))
    else:
        now_time = str(time.strftime("%Y-%m-%d %H:%M", time.localtime()))
        plt.title('From: '+ now_time + ' backward {} {}s'.format(data_quantity, freq_type))
    text_res = ax1.text(0.75, 0.9, 'Resistance: '+str(last_res), transform=ax1.transAxes)
    text_sup = ax1.text(0.75, 0.1, 'Support: '+str(last_sup), transform=ax1.transAxes)
    text_res.set_alpha(.6)
    text_sup.set_alpha(.6)
    plt.legend(loc='upper left')
    plt.ylabel('Price')
    for tick in ax1.xaxis.get_major_ticks():
        tick.label.set_fontsize(6)
    plt.savefig(newpath + '\{}.png'.format(freq_type))


def routine_generate():
    freq_types = ['day'] 
    for freq_type in  freq_types:
        #frequency = 'hour'
        ticker = 'BTC'
        data_quantity = 200
        df = get_crypto_from_api(ticker, data_quantity, freq_type)
        df['Date'] = pd.to_datetime(df['Date'])
        df = df.set_index('Date', drop=True)
        ret_df = identify(df)
        drawing(freq_type, ret_df, data_quantity)
    
def hourly_generate():
    freq_types = ['hour'] 
    for freq_type in  freq_types:
        #frequency = 'hour'
        ticker = 'BTC'
        data_quantity = 200
        df = get_crypto_from_api(ticker, data_quantity, freq_type)
        df['Date'] = pd.to_datetime(df['Date'])
        df = df.set_index('Date', drop=True)
        ret_df = identify(df)
        drawing(freq_type, ret_df, data_quantity)

def minute_generate():
    frequency = 'minute'
    ticker = 'BTC'
    intervals = [5,15]
    data_quantity = 2000
    df = get_crypto_from_api(ticker, data_quantity, frequency)
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.set_index('Date', drop=True)
    
    for interval in intervals:
        df2 = df.resample('{}min'.format(interval)).agg({'Open': 'first', 'High': 'max', 'Low': 'min', 'Close': 'last'})
        data_quantity = len(df2)
        if data_quantity > 200:
            data_quantity = 200
        ret_df = identify(df2)
        drawing(str(interval)+frequency, ret_df, data_quantity)


if __name__=='__main__':
    #routine_generate()
    hourly_generate()
    #minute_generate()












