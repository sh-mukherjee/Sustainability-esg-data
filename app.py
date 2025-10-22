import pandas as pd
import numpy as np
import altair as alt
import yfinance as yf
import streamlit as st
#from IPython.display import display, HTML

#FTSE 100 holdings (United Kingdom)

dfuk = pd.read_csv('https://topforeignstocks.com/wp-content/uploads/2025/01/Complete-List-of-UK-FTSE-100-Index-Constituents-Jan-7-2025.csv')
dfuk = dfuk.rename(columns={'Ticker (on LSE)': 'Ticker'})

#Nikkei 225 holdings (Japan)

dfjapan = pd.read_csv('https://topforeignstocks.com/wp-content/uploads/2024/01/Complete-List-of-Japan-Nikkei-225-Index-Constituents-Jan-1-2024.csv')
dfjapan = dfjapan.rename(columns={'Code': 'Ticker'})

#NASDAQ 100  (United States of America)

dfusa = pd.read_csv('https://topforeignstocks.com/wp-content/uploads/2025/01/Complete-List-of-NASDAQ-100-Constituents-Jan-4-2025.csv')

#To allow Yahoo Finance to find the tickers, we need to modify the ticker codes in the UK and Japan dataframes.
#UK tickers need to have '.L', Japan tickers need to have '.T' added at the end.

dfuk['Ticker'] = dfuk['Ticker'].astype(str) + '.L'
dfjapan['Ticker'] = dfjapan['Ticker'].astype(str) + '.T'
#dfaus['Ticker'] = dfaus['Ticker'].astype(str) + '.AX'

ukstocks = dfuk['Ticker']
jpnstocks = dfjapan['Ticker']
usastocks = dfusa['Ticker']

#We will define functions to obtain the environmental, social, governance and total ESG scores of a stock from its ticker

@st.cache_data
def get_esg_data(ticker):
    """
    Fetch Sustainalytics ESG data for a given ticker via yfinance.
    Returns a pandas DataFrame (1 row) with the desired fields or NaNs if unavailable.
    """
    t = yf.Ticker(ticker)
    esg = t.sustainability
    info = t.info  # contains 'longName', etc.

    def get_value(field):
        if esg is not None and field in esg.index:
            if 'Value' in esg.columns:
                return esg.loc[field, 'Value']
            else:
                return esg.loc[field].iloc[0]
        return np.nan

    data = {
        'Ticker': ticker,
        'Name': info.get('longName', np.nan),
        'Peer Group': get_value('peerGroup'),
        'Environmental': get_value('environmentScore'),
        'Social': get_value('socialScore'),
        'Governance': get_value('governanceScore'),
        'Total ESG': get_value('totalEsg'),
        'Percentile': get_value('percentile'),
        'Controversy Level': get_value('highestControversy'),
    }

    return pd.DataFrame([data])  # wrap dict in list → one-row DataFrame




# We will display the dataframe containing the ESG scores

st.title('Sustainalytics ESG Risk Scores')
st.sidebar.title('Choose Stock Market')
market = st.sidebar.selectbox('Country',['UK','Japan','USA'])

# Define a function to choose the appropriate list of tickers according to the country chosen above
def stocklist(country):
    if country == 'UK':
        return ukstocks
    elif country == 'Japan':
        return jpnstocks
    else:
        return usastocks

tkr = st.sidebar.selectbox('Select the ticker:', stocklist(market))
df = get_esg_data(tkr)
st.table(df, border=True)

chart1 = alt.Chart(df).mark_bar().encode(
    alt.Y('Ticker:N'),
    alt.X('Total ESG:Q',
        scale=alt.Scale(domain=(0,100))
    ),
    color=alt.Color('Total ESG:Q', scale=alt.Scale(domain = (0,100), scheme='yellowgreenblue')),
    tooltip = [alt.Tooltip('Name:N'),
               alt.Tooltip('Total ESG:Q')
              ]
)

chart2 = alt.Chart(df).mark_bar().encode(
    alt.X('Percentile:Q',
        scale=alt.Scale(domain=(0,100))
    ),
    alt.Y('Ticker:N'),
    color=alt.Color('Percentile:Q', scale=alt.Scale(domain = (0,100), scheme='yellowgreenblue')),
    tooltip = [alt.Tooltip('Name:N'),
               alt.Tooltip('Percentile:Q')
              ]
)

chart3 = alt.Chart(df).mark_bar().encode(
    alt.Y('Ticker:N'),
    alt.X('Controversy Level:Q',
        scale=alt.Scale(domain=(0,5))
    ),
    color=alt.Color('Controversy Level:Q', scale=alt.Scale(domain = (0,5), scheme='yellowgreenblue')),
    tooltip = [alt.Tooltip('Name:N'),
               alt.Tooltip('Controversy Level:Q')
              ]
)

dfesg = df[['Ticker', 'Name', 'Environmental', 'Social', 'Governance']].copy()

domain = ['Environmental', 'Social', 'Governance']
range_ = ['#17becf', '#e7969c', '#ffed6f']

chart4 = alt.Chart(dfesg,title=dfesg['Name'][0]).transform_fold(
    ['Environmental', 'Social', 'Governance'],
    as_=['Attribute', 'Scores']).mark_bar().encode(
    alt.Y('Ticker:N'),
    alt.X('Scores:Q'),
    color=alt.Color('Attribute:N').scale(domain=domain, range=range_),
    tooltip = [alt.Tooltip('Name:N'),
               alt.Tooltip('Attribute:N'),
               alt.Tooltip('Scores:Q')
              ]
    )

st.altair_chart(alt.vconcat(chart4, chart1, chart2, chart3), use_container_width=True)
