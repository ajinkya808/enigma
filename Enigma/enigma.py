import pandas as pd
import numpy as np
import xlrd
from selenium import webdriver
from selenium.webdriver.support import ui
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import os
import time
import logging


class enigma:
    def __init__(self, operating_dir, chromeDriver_dir, exclude_stocks):

        # Read Trendlyne sheet
        trendlyne_supportview = pd.read_excel(operating_dir+"\\Trendlyn_workflow\\Your Watch List  Performance view - Trendlyne.xlsx", header=1, usecols=[
                                              1, 2, 3, 4, 5, 6, 7, 11, 12, 13, 14, 15, 16, 17, 18,20,21,22,23], names=['Instrument', 'class', 's1', 's2', 's3', 'r1', 'volatility', 'D', 'M', 'V', 'Week', 'Month', '2Yr', '3Yr', '5Yr','Sector','1Yr','Target Rs.','Target %'])
        
        # Zerodha Sheet read
        zerodha_holdings = pd.read_csv(operating_dir+"\\Zerodha_workflow\\holdings.csv", usecols=[0, 1, 2, 3])
        zerodha_holdings['Investment'] = zerodha_holdings['Qty.'] * zerodha_holdings['Avg. cost']
        zerodha_holdings['Current'] = zerodha_holdings['Qty.'] * zerodha_holdings['LTP']
        zerodha_holdings['P&L'] = zerodha_holdings['Current'] - zerodha_holdings['Investment']
        zerodha_holdings['%P&L'] = round(zerodha_holdings['P&L']*100/zerodha_holdings['Investment'], 1)
        temp = pd.read_csv(operating_dir+"\\Zerodha_workflow\\holdings.csv", usecols=[7])
        zerodha_holdings['Day'] = temp['Day chg.']
        
        # merge the two sheets and round as well as fillna
        support_resistance = zerodha_holdings.merge(
            trendlyne_supportview, how='left', on='Instrument')
        
        support_resistance[['s1', 's2', 's3', 'r1']] = np.round(
            support_resistance[['s1', 's2', 's3', 'r1']], 1)
        
        support_resistance[['D', 'M','V']] = np.round(
            support_resistance[['D', 'M','V']], 2)
        
        support_resistance[['Day', 'Week', 'Month','1Yr', '2Yr', '3Yr', '5Yr',]] = np.round(support_resistance[['Day', 'Week', 'Month','1Yr', '2Yr', '3Yr', '5Yr']], 1)

        support_resistance[['D', 'V', 'M', 'volatility', 'Week', 'Month', '2Yr', '3Yr', '5Yr','Target Rs.','Target %']] = support_resistance[[
            'D', 'V', 'M', 'volatility', 'Week', 'Month', '2Yr', '3Yr', '5Yr','Target Rs.','Target %']].fillna(0)
        
        self.temp = support_resistance

        # StopLoss Estimator

        support_resistance['Stop Loss'] = support_resistance['s3'] * (1-((support_resistance['volatility'])/100))
        support_resistance['%Loss'] = (
            support_resistance['Stop Loss']-support_resistance['Avg. cost'])*100/support_resistance['Avg. cost']
        support_resistance['Loss'] = support_resistance['Stop Loss'] - support_resistance['Avg. cost']

        # Rearrange columns
        support_resistance = support_resistance[['Instrument', 'Qty.', 'Avg. cost', 'LTP', 'Investment', 'Current', 'P&L','%P&L','Day', 'Week', 'Month','1Yr', '2Yr', '3Yr', '5Yr',
                                                     's1', 's2', 's3', 'r1', 'volatility', 'Stop Loss', '%Loss', 'Loss','D', 'M', 'V', 'class','Sector','Target Rs.','Target %']]
        # Exclude stocks
        for x in exclude_stocks:
            support_resistance.drop(
                support_resistance[support_resistance['Instrument'] == x].index, axis=0, inplace=True)

        # rounding of columns
        support_resistance[['Stop Loss', '%Loss', 'Loss']] = round(
            support_resistance[['Stop Loss', '%Loss', 'Loss']], 1)

        # styling og the final sheet

        s = support_resistance.style.applymap(durability, subset=['D']).applymap(
            valuation, subset=['V']).applymap(momentum, subset=['M']).set_precision(2)
        s.applymap(volatility, subset=['volatility'])
        s.apply(highlights, axis=None)
        self.data = s.hide_index()


def volatility(vol):
    color = 'red' if vol > 0.5 else 'black'
    return 'color: %s' % color


def durability(d):
    if (d > 55):
        return 'background-color: #ccff99'
    elif (d <= 55) & (d > 35):
        return 'background-color: yellow'
    elif (d <= 35):
        return 'background-color: #b30000'


def valuation(v):
    if (v > 50):
        return 'background-color: #ccff99'
    elif (v <= 50) & (v > 30):
        return 'background-color: yellow'
    elif (v <= 30):
        return 'background-color: #b30000'


def momentum(m):
    if (m > 60):
        return 'background-color: #ccff99'
    elif (m <= 60) & (m > 35):
        return 'background-color: yellow'
    elif (m <= 35):
        return 'background-color: #b30000'


def highlights(df1):

    #Color defination
    g1 = 'background-color: #ddffbc'
    g2 = 'background-color: #bfdcae'
    g3 = 'background-color: #81b214'
    c2 = ''

    r1 = 'background-color: #eccccc'
    r2 = 'background-color: #d99999'
    r3 = 'background-color: #bb0029'

    y1 = 'background-color: yellow'
    o1 = 'background-color: #ffb270'
    
    # Current column
    # compare columns
    mask = df1['Current'] > df1['Investment']
    # DataFrame with same index and columns names as original filled empty strings
    df_ret = pd.DataFrame(c2, index=df1.index, columns=df1.columns)
    # modify values of df_ret column by boolean mask
    df_ret.loc[mask, 'Current'] = g1

    # %P&L columns
    mask = df1['%P&L'] < -5
    df_ret.loc[mask, '%P&L'] = r1
    mask = df1['%P&L'] < -10
    df_ret.loc[mask, '%P&L'] = r2
    mask = df1['%P&L'] < -15
    df_ret.loc[mask, '%P&L'] = r3

    mask = df1['%P&L'] > 7
    df_ret.loc[mask, '%P&L'] = g1
    mask = df1['%P&L'] > 15
    df_ret.loc[mask, '%P&L'] = g2
    mask = df1['%P&L'] > 22
    df_ret.loc[mask, '%P&L'] = g3
    df_ret.loc[mask,'P&L'] = g1


    # Support columns
    mask = df1['s1'] > df1['LTP']
    df_ret.loc[mask, 's1'] = r1
    mask = df1['s2'] > df1['LTP']
    df_ret.loc[mask, 's2'] = r1
    mask = df1['s3'] > df1['LTP']
    df_ret.loc[mask, 's3'] = r3

    # Resistance column
    mask = df1['r1'] < df1['LTP']
    df_ret.loc[mask, 'r1'] = g1

    # loss highlights
    mask = df1['LTP'] < df1['Avg. cost']
    df_ret.loc[mask, ['LTP', 'Investment', 'Current', 'P&L']] = r1

    # StopLoss highlights
    mask = df1['Stop Loss'] < df1['Avg. cost']
    df_ret.loc[mask, 'Stop Loss'] = r1

    #% change hightlights
    dl1=0
    dl2=-5
    dl3=-15

    #Day highlights
    mask = df1['Day'] < dl1
    df_ret.loc[mask, 'Day'] = r1
    
    mask = df1['Day'] < dl2
    df_ret.loc[mask, 'Day'] = r2
    
    mask = df1['Day'] < dl3
    df_ret.loc[mask, 'Day'] = r3

    # Week highlights
    mask = df1['Week'] < dl1
    df_ret.loc[mask, 'Week'] = r1
    
    mask = df1['Week'] < dl2
    df_ret.loc[mask, 'Week'] = r2

    mask = df1['Week'] < dl3
    df_ret.loc[mask, 'Week'] = r3

    # Month highlights
    mask = df1['Month'] < dl1
    df_ret.loc[mask, 'Month'] = r1
    
    mask = df1['Month'] < dl2
    df_ret.loc[mask, 'Month'] = r2

    mask = df1['Month'] < dl3
    df_ret.loc[mask, 'Month'] = r3
    
    # 1Yr highlights
    mask = df1['1Yr'] < dl1
    df_ret.loc[mask, '1Yr'] = r1
    
    mask = df1['1Yr'] < dl2
    df_ret.loc[mask, '1Yr'] = r2

    mask = df1['1Yr'] < dl3
    df_ret.loc[mask, '1Yr'] = r3

    # 2Yr highlights
    mask = df1['2Yr'] < dl1
    df_ret.loc[mask, '2Yr'] = r1
    
    mask = df1['2Yr'] < dl2
    df_ret.loc[mask, '2Yr'] = r2

    mask = df1['2Yr'] < dl3
    df_ret.loc[mask, '2Yr'] = r3


    # 3Yr highlights
    mask = df1['3Yr'] < dl1
    df_ret.loc[mask, '3Yr'] = r1
    
    mask = df1['3Yr'] < dl2
    df_ret.loc[mask, '3Yr'] = r2

    mask = df1['3Yr'] < dl3
    df_ret.loc[mask, '3Yr'] = r3

    # 5Yr highlights
    mask = df1['5Yr'] < dl1
    df_ret.loc[mask, '5Yr'] = r1
    
    mask = df1['5Yr'] < dl2
    df_ret.loc[mask, '5Yr'] = r2

    mask = df1['5Yr'] < dl3
    df_ret.loc[mask, '5Yr'] = r3
    

    # class highlishts
    mask=[]
    for x in df1['class']:
        if x in ['Value Stock. Under Radar', 'Expensive Star']:
            mask.append(True)
        else: mask.append(False)

    df_ret.loc[mask,'class']=g1
    
    mask=[]
    for x in df1['class']:
        if x in ['Strong Performer','Strong Performer, Under Radar','Strong Performer, Getting Expensive']:
            mask.append(True)
        else: mask.append(False)
    
    df_ret.loc[mask,'class']=g3

    mask=[]
    for x in df1['class']:
        if x in ['Expensive Performer', 'Mid-range Performer', 'Expensive Underperformer','Slowing Down Stock','Turnaround Potential','Expensive Performer','Expensive Rocket']:
            mask.append(True)
        else: mask.append(False)
    
    df_ret.loc[mask,'class']=y1
    
    
    mask=[]
    for x in df1['class']:
        if x in ['Expensive Rocket']:
            mask.append(True)
        else: mask.append(False)
    
    df_ret.loc[mask,'class']=o1

    
    mask=[]
    for x in df1['class']:
        if x in ['Falling Comet','Value Trap','Risky Value','Momentum Trap','Weak Stock','Await Turnaround']:
            mask.append(True)
        else: mask.append(False)
    
    df_ret.loc[mask,'class']=r3

    
    
    return df_ret