# -*- coding: utf-8 -*-
"""BigData_FinalAssignment.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1CQi4zvTGGxhBsv8hNVCeUsDtjlBco6K1

#1. 기초적인 라이브러리 import 및 install
"""

!pip install ace_tools_open

!pip install fredapi pandas

import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import skew, kurtosis
import seaborn as sns

"""# 2. 위키피디아에서 Ticker 와 Sector 를 가져와, 매칭한 정보를 데이터프레임으로"""

# Fetch the list of S&P 500 companies from Wikipedia
url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
tables = pd.read_html(url)
sp500_table = tables[0]

# Extract ticker symbols and sectors
tickers = sp500_table['Symbol'].tolist()
sectors = sp500_table['GICS Sector'].tolist()

# Create a DataFrame
sp500_df = pd.DataFrame({'Ticker': tickers, 'Sector': sectors})

print(sp500_df)
sp500_df.to_csv("sp500_tickers.csv", index=False)

"""## Ticker 를 리스트로 만든 다음, yfinance 를 통해 Sector 정보를 가져온다. <br>혹시 위키피디아와 yfinance 가 다를 수 있기 때문"""

ticker_list = sp500_df['Ticker'].values.tolist()

# Fetch sector information
sector_data = {}
for ticker in ticker_list:
    try:
        stock = yf.Ticker(ticker)
        sector_data[ticker] = stock.info.get('sector', 'Unknown')
    except Exception as e:
        print(f"Error fetching data for {ticker}: {e}")

# Convert to DataFrame
sector_df = pd.DataFrame(list(sector_data.items()), columns=['Ticker', 'Sector'])

print(sector_df)

"""## 섹터들의 리스트를 가져온다"""

sector_list = sector_df['Sector'].unique()

print(sector_list)

sector_df['Sector'].value_counts()

"""## 이후, 앞에서 구했던 ticker_list 를 바탕으로 yfinance 에서 2013-01-01 부터 2023-12-31, 약 10년의 일일 가격 정보를 가져온다."""

# Download historical data
start_date = "2013-01-01"
end_date = "2023-12-31"

# Fetch daily data for all tickers
data = yf.download(ticker_list, start=start_date, end=end_date)['Adj Close']

data.head()

"""## 결측치 확인 및 제거"""

data.isnull().sum()

sp500_ver2 = data.dropna(axis=1)

"""## 결측치 삭제 한 값으로 일일 수익률 생성<br>
- 이 때, pd.to_datetime 을 통해 Date 확보가 중요하다. 이후에 시계열 데이터로 표현해야 하기 때문.
"""

sp500_ver2.to_csv("sp500_ver2.csv")

# Ensure the 'Date' column is in datetime format and set it as the index
# 중간에 엑셀로 다운받은 뒤 재 업로드. 그래서 파일명이 달라졌다.
# dateTime 으로 Date 를 설정한 후, 이를 index 로 설정한다.
sp500_ver3 = pd.read_csv('/content/sp500_ver2.1_.csv')
sp500_ver3['Date'] = pd.to_datetime(sp500_ver3['Date'])
sp500_ver3.set_index('Date', inplace=True)

# Calculate daily returns
daily_returns = sp500_ver3.pct_change().dropna()

# Reset index for better usability
daily_returns.reset_index(inplace=True)

# 좀 더 가독성 좋게 표현해주는 도구.
import ace_tools_open as tools; tools.display_dataframe_to_user(name="Daily Returns Data", dataframe=daily_returns)

# Show a sample of the daily returns data
daily_returns.head()

"""## 이제 본격적으로 섹터 별 분리를 시작한다.

- 일일 수익률 표의 Ticker 들 추출<br>
- 이거를 섹터별로 분리 후, 분리된 티커들을 바탕으로 수익률들도 분리하자
"""

daily_returns = pd.read_csv("/content/daily_returns.csv")
new_tickers = daily_returns.columns.unique().to_list()

# Fetch sector information
sector_data = {}
for ticker in new_tickers:
    try:
        stock = yf.Ticker(ticker)
        sector_data[ticker] = stock.info.get('sector', 'Unknown')
    except Exception as e:
        print(f"Error fetching data for {ticker}: {e}")

# Convert to DataFrame
sector_df = pd.DataFrame(list(sector_data.items()), columns=['Ticker', 'Sector'])

daily_returns.head()

"""## 확보한 sector_df 를 바탕으로,
- 특정 섹터만 column 을 기준으로 별도의 데이터프레임으로 분리<br>
- Technology 섹터에 진행한 후, 같은 방법으로 다른 섹터들도 분리해준다.
"""

tech_rows = sector_df[sector_df['Sector'] == 'Technology']
tech_tickers = tech_rows['Ticker'].to_list()
tech_ret = daily_returns[np.intersect1d(daily_returns.columns, tech_tickers)]

tech_ret.to_csv("tech_ret.csv")

tech_ret.head()

#Date 가 생략되었기에, 이를 추가해준다.
tech_ret['Date'] = daily_returns['Date'].to_numpy()

tech_ret.head()

"""## 이제, Technology 섹터를 분리한 것처럼, 다른 섹터들도 별개의 데이터프레임으로 분리
- 각 데이터프레임을 모두 csv 파일로 저장해준다.
"""

# List of sectors
sectors = [
    'Healthcare', 'Financial Services', 'Consumer Defensive', 'Utilities',
    'Basic Materials', 'Consumer Cyclical', 'Industrials', 'Real Estate',
    'Energy', 'Communication Services'
]

# Loop through each sector and create a DataFrame for its daily returns
for sector in sectors:
    # Filter rows for the specific sector
    sector_rows = sector_df[sector_df['Sector'] == sector]
    # Get the tickers for the sector
    sector_tickers = sector_rows['Ticker'].to_list()
    # Filter daily returns for these tickers
    sector_ret = daily_returns[np.intersect1d(daily_returns.columns, sector_tickers)]
    # Save the resulting DataFrame
    sector_ret.to_csv(f"{sector}_daily_returns.csv", index=False)
    print(f"Saved {sector}_daily_returns.csv")

"""## 여기서부터 큰 실수를 했다.
- 쓸데없이 이름을 복잡하게 하고, 전처리를 다 하지 않은 상태로 분리해버려 일일히 노가다를 했다.<br>
- 시간 추가, 값들 모두 숫자값으로 변경
"""

Financial_Services_daily_returns = pd.read_csv("Financial Services_daily_returns.csv")
Consumer_Defensive_daily_returns = pd.read_csv("Consumer Defensive_daily_returns.csv")
Utilities_daily_returns = pd.read_csv("Utilities_daily_returns.csv")
Basic_Materials_daily_returns = pd.read_csv("Basic Materials_daily_returns.csv")
Consumer_Cyclical_daily_returns = pd.read_csv("Consumer Cyclical_daily_returns.csv")
Industrials_daily_returns = pd.read_csv("Industrials_daily_returns.csv")
Real_Estate_daily_returns = pd.read_csv("Real Estate_daily_returns.csv")
Energy_daily_returns = pd.read_csv("Energy_daily_returns.csv")
Communication_Services_daily_returns = pd.read_csv("Communication Services_daily_returns.csv")
Healthcare_daily_returns = pd.read_csv('Healthcare_daily_returns.csv')

Financial_Services_daily_returns['Date'] = daily_returns['Date'].to_numpy()
Consumer_Defensive_daily_returns['Date'] = daily_returns['Date'].to_numpy()
Utilities_daily_returns['Date'] = daily_returns['Date'].to_numpy()
Basic_Materials_daily_returns['Date'] = daily_returns['Date'].to_numpy()
Consumer_Cyclical_daily_returns['Date'] = daily_returns['Date'].to_numpy()
Industrials_daily_returns['Date'] = daily_returns['Date'].to_numpy()
Real_Estate_daily_returns['Date'] = daily_returns['Date'].to_numpy()
Energy_daily_returns['Date'] = daily_returns['Date'].to_numpy()
Communication_Services_daily_returns['Date'] = daily_returns['Date'].to_numpy()
tech_ret['Date'] = daily_returns['Date'].to_numpy()
Healthcare_daily_returns["Date"] = daily_returns['Date'].to_numpy()

Financial_Services_daily_returns.set_index(keys='Date',drop=True)
Consumer_Defensive_daily_returns.set_index(keys='Date',drop=True)
Utilities_daily_returns.set_index(keys='Date',drop=True)
Basic_Materials_daily_returns.set_index(keys='Date',drop=True)
Consumer_Cyclical_daily_returns.set_index(keys='Date',drop=True)
Industrials_daily_returns.set_index(keys='Date',drop=True)
Real_Estate_daily_returns.set_index(keys='Date',drop=True)
Energy_daily_returns.set_index(keys='Date',drop=True)
Communication_Services_daily_returns.set_index(keys='Date',drop=True)
Healthcare_daily_returns.set_index(keys='Date',drop=True)
tech_ret.set_index(keys='Date',drop=True)

Financial_Services_daily_returns.to_csv("Fin_ret_1.csv")
Consumer_Defensive_daily_returns.to_csv("CD_ret_1.csv")
Utilities_daily_returns.to_csv("Util_ret_1.csv")
Basic_Materials_daily_returns.to_csv("BM_ret_1.csv")
Consumer_Cyclical_daily_returns.to_csv("CC_ret_1.csv")
Industrials_daily_returns.to_csv("Ind_ret_1.csv")
Real_Estate_daily_returns.to_csv("RE_ret_1.csv")
Energy_daily_returns.to_csv("Eng_ret_1.csv")
Communication_Services_daily_returns.to_csv("CS_ret_1.csv")
Healthcare_daily_returns.to_csv("Health_ret_1.csv")
tech_ret.to_csv("Tech_ret_1.csv")

fin = Financial_Services_daily_returns.applymap(lambda x: pd.to_numeric(x, errors='coerce'))
cd = Consumer_Defensive_daily_returns.applymap(lambda x: pd.to_numeric(x, errors='coerce'))
util = Utilities_daily_returns.applymap(lambda x: pd.to_numeric(x, errors='coerce'))
bm = Basic_Materials_daily_returns.applymap(lambda x: pd.to_numeric(x, errors='coerce'))
cc = Consumer_Cyclical_daily_returns.applymap(lambda x: pd.to_numeric(x, errors='coerce'))
ind = Industrials_daily_returns.applymap(lambda x: pd.to_numeric(x, errors='coerce'))
re = Real_Estate_daily_returns.applymap(lambda x: pd.to_numeric(x, errors='coerce'))
eng = Energy_daily_returns.applymap(lambda x: pd.to_numeric(x, errors='coerce'))
cs = Communication_Services_daily_returns.applymap(lambda x: pd.to_numeric(x, errors='coerce'))
health = Healthcare_daily_returns.applymap(lambda x: pd.to_numeric(x, errors='coerce'))
tech = tech_ret.applymap(lambda x: pd.to_numeric(x, errors='coerce'))

"""## 모든 종목을 일일히 분석하는 건 불가능하다. 그렇기에 섹터의 일자별 평균 수익률만 도출
- 이후, 이 평균 수익률을 따로 합친다.
"""

fin['Average_Return'] = fin.mean(axis=1)
cd['Average_Return'] = cd.mean(axis=1)
util['Average_Return'] = util.mean(axis=1)
bm['Average_Return'] = bm.mean(axis=1)
cc['Average_Return'] = cc.mean(axis=1)
ind['Average_Return'] = ind.mean(axis=1)
re['Average_Return'] = re.mean(axis=1)
eng['Average_Return'] = eng.mean(axis=1)
cs['Average_Return'] = cs.mean(axis=1)
health['Average_Return'] = health.mean(axis=1)
tech['Average_Return'] = tech.mean(axis=1)

final_1 = pd.concat([fin['Average_Return'], cd['Average_Return'], util['Average_Return'], bm['Average_Return'], cc['Average_Return'], ind['Average_Return'], re['Average_Return'], eng['Average_Return'], cs['Average_Return'], health['Average_Return'], tech['Average_Return']], axis=1, keys=['Financial_Services','Consumer_Defensive','Utilities','Basic_Materials','Consumer_Cyclical','Industrials','Real_Estate','Energy','Communication_Services','Healthcare','Technology'])

final_1["Date"] = daily_returns['Date'].to_numpy()
final_1.set_index(keys='Date',drop=True)

"""## 이제, 수익률과 상관관계를 분석할 요소들을 가져와 데이터프레임으로 보관한다.
- EFFR, 그리고 미국과 수출입 비중이 높은 4국가 간의 환율<br>
- FRED API 를 사용한다.
"""

from fredapi import Fred
import pandas as pd

# Replace with your FRED API key
fred_api_key = '9238680decbecf609e470c20fcc23b41'
fred = Fred(api_key=fred_api_key)

# Fetch data from FRED
effr = fred.get_series('DFF', observation_start='2013-01-03', observation_end='2023-12-29')
usd_cad = fred.get_series('DEXCAUS', observation_start='2013-01-03', observation_end='2023-12-29')
usd_mxn = fred.get_series('DEXMXUS', observation_start='2013-01-03', observation_end='2023-12-29')
usd_cny = fred.get_series('DEXCHUS', observation_start='2013-01-03', observation_end='2023-12-29')
usd_jpy = fred.get_series('DEXJPUS', observation_start='2013-01-03', observation_end='2023-12-29')

# Combine data into a DataFrame
data = pd.DataFrame({
    'EFFR': effr,
    'USD/CAD': usd_cad,
    'USD/MXN': usd_mxn,
    'USD/CNY': usd_cny,
    'USD/JPY': usd_jpy
})

# Reset index to make 'Date' a column
data.reset_index(inplace=True)
data.rename(columns={'index': 'Date'}, inplace=True)

# Save to CSV
data.to_csv('daily_effr_exchange_rates.csv', index=False)

print(data.head())

"""## 결측치는 time 을 기준으로 interpolate 함수를 이용해 채운다."""

# Ensure 'Date' column is in datetime format
data['Date'] = pd.to_datetime(data['Date'])

# Set 'Date' as the index
data.set_index('Date', inplace=True)

# Interpolate missing data using time-based interpolation
data.interpolate(method='time', inplace=True)

data.isna().sum()

"""## 이제, 최종적으로 섹터 별 주가 수익률 데이터프레임과 이자율&환율 정보를 합치기 위해 Date 를 조정한다."""

final_1.dtypes

# Ensure 'Date' column is in datetime format
final_1['Date'] = pd.to_datetime(final_1['Date'])

# Set 'Date' as the index
final_1.set_index('Date', inplace=True)

# Set 'Date' as the index for both DataFrames
IR_n_FX.set_index('Date', inplace=True)

IR_n_FX.head()

"""## 섹터 별 수익률 데이터를 기준으로 left join, merge 한다."""

# Merge the datasets, keeping all rows from final_1
merged_data = final_1.merge(IR_n_FX, how='left', left_index=True, right_index=True)

merged_data.head()

merged_data.isnull().sum()

merged_data.dtypes

"""## 시각화 단계이다.
- x축을 연도 기준으로 표시되도록 설정한다<br>

"""

import matplotlib.dates as mdates

# Ensure 'Date' is in datetime format
final['Date'] = pd.to_datetime(final['Date'])

# Plot time series for each numeric column
numeric_columns = final.iloc[:, 1:].columns

# Plot time series
for column in numeric_columns:
    plt.figure(figsize=(10, 6))
    plt.plot(final['Date'], final[column], label=column)
    plt.title(f"Time Series of {column}")
    plt.xlabel('Date')
    plt.ylabel(column)

    # Format x-axis to show only years
    plt.gca().xaxis.set_major_locator(mdates.YearLocator())  # Major ticks at each year
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y'))  # Format ticks as 'YYYY'
    plt.gca().xaxis.set_minor_locator(mdates.MonthLocator())  # Optional: Minor ticks at each month
    plt.gcf().autofmt_xdate()  # Rotate and format the x-axis labels

    plt.legend()
    plt.show()

"""## 시계열 데이터에 이어, 수익률의 분포를 나타낸다.
- 왜도, 첨도까지 표시. 확실히 다들 정규분포가 아님을 알 수 있다.
"""

# Filter sector columns (excluding non-sector numeric columns like EFFR and FX rates)
sector_columns = [col for col in numeric_columns if col not in ['EFFR', 'USD/CAD', 'USD/MXN', 'USD/CNY', 'USD/JPY']]


# Plot distribution with mean, standard deviation, skewness, and kurtosis
for column in sector_columns:
    data = final[column].dropna()
    mean_val = data.mean()
    std_val = data.std()
    skewness = skew(data)
    kurt = kurtosis(data)

    plt.figure(figsize=(10, 6))
    plt.hist(data, bins=50, alpha=0.7, label=f"{column}", color='orange')
    plt.axvline(mean_val, color='red', linestyle='dashed', linewidth=2, label=f"Mean: {mean_val:.4f}")
    plt.axvline(mean_val - std_val, color='blue', linestyle='dashed', linewidth=2, label=f"-1 SD: {mean_val - std_val:.4f}")
    plt.axvline(mean_val + std_val, color='blue', linestyle='dashed', linewidth=2, label=f"+1 SD: {mean_val + std_val:.4f}")
    plt.title(f"Distribution of {column} with Statistics")
    plt.xlabel(column)
    plt.ylabel('Frequency')
    plt.legend()
    plt.text(mean_val, plt.ylim()[1]*0.9, f"Skewness: {skewness:.4f}\nKurtosis: {kurt:.4f}", fontsize=10, color='green')
    plt.show()

"""## 앞서 시계열 자료를 보완하기 위한 추가적인 시각화"""

# Draw boxplots for all sector columns
plt.figure(figsize=(15, 8),)
plt.boxplot([final[col].dropna() for col in sector_columns], labels=sector_columns, patch_artist=True,)
plt.title("Boxplots of Sector Columns")
plt.xlabel("Sectors")
plt.ylabel("Values")
plt.xticks(rotation=45)
plt.grid(axis='y')
plt.show()

"""## 그리고 describe 를 통한 quantile 확인"""

final.iloc[:,0:11].describe()

"""## 가장 확인해보고 싶었던 상관관계. Heatmap 을 사용했다."""

# Calculate correlation between sectors' daily returns and EFFR
effr_corr = final[sector_columns + ['EFFR']].corr()['EFFR'].drop('EFFR')

# Calculate correlation between sectors' daily returns and currency exchange rates
fx_columns = ['USD/CAD', 'USD/MXN', 'USD/CNY', 'USD/JPY']
fx_corr = final[sector_columns + fx_columns].corr()

# Extract correlations for FX rates with sectors
fx_corr_sectors = fx_corr.loc[sector_columns, fx_columns]

# Plot heatmap for correlation with EFFR
plt.figure(figsize=(10, 6))
sns.heatmap(effr_corr.to_frame(name="EFFR Correlation"), annot=True, cmap='coolwarm', cbar=True)
plt.title("Correlation Between Sectors and EFFR")
plt.show()

# Plot heatmap for correlation with FX rates
plt.figure(figsize=(12, 8))
sns.heatmap(fx_corr_sectors, annot=True, cmap='coolwarm', cbar=True)
plt.title("Correlation Between Sectors and Currency Exchange Rates")
plt.show()