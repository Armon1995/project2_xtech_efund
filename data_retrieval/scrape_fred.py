"""
Created on Sat Mar 1 14:30:59 2024

Author: davideliu

E-mail: davide97ls@gmail.com

Goal: Scrape FRED data and Yahoo Finance data
"""
import pandas as pd
from pandas_datareader import data as pdr
import yfinance as yf
from datetime import datetime


# Define FRED series IDs for the required indicators
fred_series = {
    'China_GDP': 'MKTGDPCNA646NWDB',
    'China_Inflation': 'FPCPITOTLZGCHN',
    'China_Unemployment_Rate': 'SLUEM1524ZSCHN',
    'China_Public_Debt': 'GGGDTACNA188N',
    'China_Gov_Lending': 'GGNLBACNA188N',
    'US_Interest_Rates': 'DFF',
    'US_Composite_Leading_Indicator': 'USALOLITONOSTSAM',
    'China_Composite_Leading_Indicator': 'CHNLOLITONOSTSAM',
    'China_Business_Confidence': 'BSCICP03CNM665S',
}

# Define Yahoo Finance symbols for stock indices
yahoo_series = {
    'Shanghai_Composite': '000001.SS',
    'CNYUSD': 'CNYUSD=X',
    'CNYEUR': 'CNYEUR=X'
}


# Function to download data from FRED using pandas_datareader
def download_fred_data(series_dict, start, end):
    """
    Download financial time series data from FRED.

    Parameters:
    - series_dict (dict): Dictionary mapping series names to their FRED IDs.
    - start (str): Start date (YYYY-MM-DD).
    - end (str): End date (YYYY-MM-DD).

    Returns:
    - pd.DataFrame: FRED data in monthly frequency.
    """
    fred_data = pd.DataFrame()
    for name, series_id in series_dict.items():
        try:
            # Fetch data from FRED
            data = pdr.get_data_fred(series_id, start=start, end=end)
            data = data.resample('M').last()  # Resample to monthly frequency

            # Calculate percentage change for GDP (not done anymore)
            if name == 'China_GDP':
                data[series_id] = data[series_id] / 1000000000000.

            fred_data[name] = data[series_id]
            print(f"Downloaded {name} from FRED")
        except Exception as e:
            print(f"Error downloading {name}: {e}")
    return fred_data


# Function to download data from Yahoo Finance using yfinance
def download_yahoo_data(symbols, start):
    """
    Download historical data from Yahoo Finance.

    Parameters:
    - symbols (dict): Dictionary mapping asset names to Yahoo Finance tickers.
    - start (str): Start date (YYYY-MM-DD).

    Returns:
    - pd.DataFrame: Yahoo Finance data in monthly frequency.
    """
    yahoo_data = pd.DataFrame()
    for name, symbol in symbols.items():
        try:
            # Fetch historical data from Yahoo Finance
            data = yf.download(symbol, start=start, interval='1mo')['Close']
            data.name = name
            yahoo_data[name] = data
            print(f"Downloaded {name} from Yahoo Finance")
        except Exception as e:
            print(f"Error downloading {name}: {e}")
    return yahoo_data


def update_data_fred(start_date='2016-01-01', end_date=None, file_path=f'data/X_data_Fred.csv'):
    """
    Fetch and update financial data from FRED and Yahoo Finance.

    Parameters:
    - start_date (str, optional): Start date (default is '2016-01-01').
    - end_date (str, optional): End date (default is today).
    - file_path (str, optional): File path for saving the output CSV.

    Returns:
    - None: Saves the file locally.
    """
    if end_date is None:
        end_date = datetime.today().strftime('%Y-%m-%d')
    # Download data from both FRED and Yahoo Finance
    fred_data = download_fred_data(fred_series, start_date, end_date)
    yahoo_data = download_yahoo_data(yahoo_series, start_date)
    combined_data = pd.concat([fred_data, yahoo_data], axis=1)
    combined_data = combined_data.resample('M').last()

    # Save the data to a CSV file
    combined_data.to_csv(file_path)


if __name__ == '__main__':
    update_data_fred()
    print('Fred和Yahoo数据更新完成')
