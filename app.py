# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import pandas as pd
import numpy as np
import altair as alt
import yfinance as yf
import streamlit as st
#from IPython.display import display, HTML

#FTSE 100 holdings (United Kingdom)
dfuk = pd.read_excel('https://topforeignstocks.com/wp-content/uploads/2021/01/UK-FTSE-100-Index-Constituents-List-Jan-2021-New.xlsx', engine='openpyxl')

#ASX holdings (Australia)
dfaus = pd.read_excel('https://topforeignstocks.com/wp-content/uploads/2021/01/Australia-ASX-200-Index-Constituents-List-Jan-2021.xlsx', engine='openpyxl')

#Nikkei 225 holdings (Japan)
dfjapan = pd.read_excel('https://topforeignstocks.com/wp-content/uploads/2020/01/Complete-List-of-Constituents-of-Nikkei-225-Jan-2020-Original.xlsx', engine='openpyxl')

#S&P 500  (United States of America)
dfusa = pd.read_excel('https://topforeignstocks.com/wp-content/uploads/2021/01/SP-500-Index-Constituents-List-Jan-1-2021.xlsx', engine='openpyxl')

#To allow Yahoo Finance to find the tickers, we need to modify the ticker codes in the UK, Germany, Japan and Australia dataframes.
#UK tickers need to have '.L', Japan tickers need to have '.T', and Australia tickers need to have '.AX' added at the end.

dfuk['Ticker'] = dfuk['Ticker'].astype(str) + '.L'
dfjapan['Ticker'] = dfjapan['Ticker'].astype(str) + '.T'
dfaus['Ticker'] = dfaus['Ticker'].astype(str) + '.AX'

ukstocks = dfuk['Ticker']
jpnstocks = dfjapan['Ticker']
ausstocks = dfaus['Ticker']
usastocks = dfusa['Ticker']

#We will define functions to obtain the environmental, social, governance and total ESG scores of a stock from its ticker

def env(ticker):
    if yf.Ticker(ticker).sustainability is not None:
        return yf.Ticker(ticker).sustainability.loc['environmentScore','Value']
    else:
        return np.NaN

def social(ticker):
    if yf.Ticker(ticker).sustainability is not None:
        return yf.Ticker(ticker).sustainability.loc['socialScore','Value']
    else:
        return np.NaN

def gov(ticker):
    if yf.Ticker(ticker).sustainability is not None:
        return yf.Ticker(ticker).sustainability.loc['governanceScore','Value']
    else:
        return np.NaN
    
def total(ticker):
    if yf.Ticker(ticker).sustainability is not None:
        return yf.Ticker(ticker).sustainability.loc['totalEsg','Value']
    else:
        return np.NaN

def percentile(ticker):
    if yf.Ticker(ticker).sustainability is not None:
        return yf.Ticker(ticker).sustainability.loc['percentile', 'Value']
    else:
        return np.Nan    

def contro(ticker):
    if yf.Ticker(ticker).sustainability is not None:
        return yf.Ticker(ticker).sustainability.loc['highestControversy','Value']
    else:
        return np.NaN
    
 # We will define a function that combines these scores into a dataframe

def scores(ticker):
    return pd.DataFrame([[ticker,yf.Ticker(ticker).info['longName'],env(ticker),social(ticker),gov(ticker),total(ticker),percentile(ticker),contro(ticker)]],columns=['Ticker','Name','Environmental','Social','Governance','Total ESG','Percentile','Controversy Level'])

# We will display the dataframe containing the ESG scores

#tkr = 'MSFT'
st.title('Sustainalytics ESG Risk Scores')
st.sidebar.title('Choose Stock Market')
market = st.sidebar.selectbox('Country',['UK','Japan','Australia','USA'])

# Define a function to choose the appropriate list of tickers according to the country chosen above
def stocklist(country):
    if country == 'UK':
        return ukstocks
    elif country == 'Japan':
        return jpnstocks
    elif country == 'Australia':
        return ausstocks
    else:
        return usastocks

tkr = st.sidebar.selectbox('Select the ticker:', stocklist(market))
df = scores(tkr)
#display(HTML(df.to_html()))

chart1 = alt.Chart(df).mark_bar().encode(
    alt.Y('Ticker:N'),
    alt.X('Total ESG:Q',
        scale=alt.Scale(domain=(0,100))
    ),
    color=alt.Color('Total ESG:Q', scale=alt.Scale(domain = (0,100), scheme='yellowgreenblue')),
    tooltip = [alt.Tooltip('Name:N'),
               alt.Tooltip('Total ESG:Q')
              ]
).interactive()

chart2 = alt.Chart(df).mark_bar().encode(
    alt.X('Percentile:Q',
        scale=alt.Scale(domain=(0,100))
    ),
    alt.Y('Ticker:N'),
    color=alt.Color('Percentile:Q', scale=alt.Scale(domain = (0,100), scheme='yellowgreenblue')),
    tooltip = [alt.Tooltip('Name:N'),
               alt.Tooltip('Percentile:Q')
              ]
).interactive()

chart3 = alt.Chart(df).mark_bar().encode(
    alt.Y('Ticker:N'),
    alt.X('Controversy Level:Q',
        scale=alt.Scale(domain=(0,5))
    ),
    color=alt.Color('Controversy Level:Q', scale=alt.Scale(domain = (0,5), scheme='yellowgreenblue')),
    tooltip = [alt.Tooltip('Name:N'),
               alt.Tooltip('Controversy Level:Q')
              ]
).interactive()

dfesg = df[['Ticker', 'Name','Environmental', 'Social', 'Governance']].copy()

chart4 = alt.Chart(dfesg,title=dfesg['Name'][0]).transform_fold(
    ['Environmental', 'Social', 'Governance'],
    as_=['Attribute', 'Scores']).mark_bar().encode(
    alt.Y('Ticker:N'),
    alt.X('Scores:Q'),
    color='Attribute:N',
    tooltip = [alt.Tooltip('Name:N'),
               alt.Tooltip('Attribute:N'),
               alt.Tooltip('Scores:Q')
              ]
    ).interactive()

#alt.vconcat(chart4, chart1, chart2, chart3)

st.altair_chart(alt.vconcat(chart4, chart1, chart2, chart3), use_container_width=True)
