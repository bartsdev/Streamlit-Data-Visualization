import base64

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
import yfinance as yf

st.set_page_config(layout="wide")

st.title('S&P 500 App with Filters')

st.markdown("""
This app retrieves the list of the **S&P 500** (from Wikipedia) and its corresponding **stock closing price** (year-to-date)!
* **Python libraries:** base64, pandas, streamlit, numpy, matplotlib, seaborn
* **Data source:** [Wikipedia](https://en.wikipedia.org/wiki/List_of_S%26P_500_companies).
""")

st.sidebar.header('User Input Features')

# Web scraping of S&P 500 data
#
@st.cache
def load_data():
    url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
    html = pd.read_html(url, header = 0)
    df = html[0]
    return df

df = load_data()
sector = df.groupby('GICS Sector')

# Sidebar - Sector selection

ticker_time_range = ['1d','5d','1mo','3mo','6mo','1y','2y','5y','10y','ytd','max']
time_period = st.sidebar.selectbox('Time Period', ticker_time_range)

sorted_symbol_unique = sorted( df['Symbol'].unique())
selected_symbol = st.sidebar.selectbox('Symbol Name', sorted_symbol_unique)

sorted_sector_unique = sorted( df['GICS Sector'].unique())
selected_sector = st.sidebar.multiselect('Sector Name', sorted_sector_unique,sorted_sector_unique)

sorted_subsector_unique = sorted(df['GICS Sub-Industry'].unique())
selected_subsector = st.sidebar.multiselect('Sub-Industry Name', sorted_subsector_unique)

# Filtering data
if selected_sector and not selected_subsector:
    df_selected_sector = df[ (df['GICS Sector'].isin(selected_sector)) & (df['GICS Sub-Industry'].isin(
        sorted_subsector_unique))]
elif selected_sector and selected_subsector:
    df_selected_sector = df[ (df['GICS Sector'].isin(selected_sector)) & (df['GICS Sub-Industry'].isin(
        selected_subsector))]
elif not selected_sector and selected_subsector:
    df_selected_sector = df[(df['GICS Sector'].isin(sorted_sector_unique)) & df['GICS Sub-Industry'].isin(
        selected_subsector)]
else:
    df_selected_sector = df[ (df['GICS Sector'].isin(sorted_sector_unique)) & (df['GICS Sub-Industry'].isin(sorted_subsector_unique))]


st.header('Display Companies in Selected Sector')
st.write('Data Dimension: ' + str(df_selected_sector.shape[0]) + ' rows and ' + str(df_selected_sector.shape[1]) + ' columns.')
st.dataframe(df_selected_sector)

# Download S&P500 data
# https://discuss.streamlit.io/t/how-to-download-file-in-streamlit/1806
def filedownload(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # strings <-> bytes conversions
    href = f'<a href="data:file/csv;base64,{b64}" download="SP500.csv">Download CSV File</a>'
    return href

st.markdown(filedownload(df_selected_sector), unsafe_allow_html=True)

# https://pypi.org/project/yfinance/


if not df_selected_sector.empty:
    data = yf.download(
    tickers = list(df_selected_sector[:10].Symbol),
    period = time_period,
    interval = "15m",
    group_by = 'ticker',
    auto_adjust = True,
    prepost = True,
    threads = True,
    proxy = None
)

# Plot Closing Price of Query Symbol
def price_plot(symbol):
  df = pd.DataFrame(data[symbol].Close)
  df['Date'] = df.index
  fig, ax = plt.subplots()
  plt.fill_between(df.Date, df.Close, color='skyblue', alpha=0.3)
  plt.plot(df.Date, df.Close, color='skyblue', alpha=0.8)
  plt.xticks(rotation=90)
  plt.title(symbol, fontweight='bold')
  plt.xlabel('Date', fontweight='bold')
  plt.ylabel('Closing Price', fontweight='bold')
  return st.pyplot(fig)

num_company = st.sidebar.slider('Number of Companies', 1, 5)

if st.button('Show Plots'):
    st.header('Stock Closing Price')
    for i in list(df_selected_sector.Symbol)[:num_company]:
        price_plot(i)
