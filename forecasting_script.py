# Part 1
import os
import warnings
warnings.filterwarnings('ignore')
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.tsa.stattools import adfuller
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.arima.model import ARIMA  # Updated import path
import pmdarima as pm  # Simplified import for auto_arima
from sklearn.metrics import mean_squared_error, mean_absolute_error
import math
import requests
from datetime import datetime, timedelta


def predict_stock_price(ticker):
    dateparse = lambda dates: pd.to_datetime(dates, format='%Y-%m-%d')
    stock_data = pd.read_csv(f'data/historical_stock_price/{ticker}.csv', sep=',', index_col='Date', parse_dates=['Date'], date_parser=dateparse).fillna(0)

    df_close = stock_data['Close']

    from pylab import rcParams
    rcParams['figure.figsize'] = 10, 6
    df_log = np.log(df_close)

    train_data = df_log

    # Part 7
    model_autoARIMA = pm.auto_arima(train_data, start_p=0, start_q=0,
                        test='adf',       # Use adftest to find optimal 'd'
                        max_p=3, max_q=3, # Maximum p and q
                        m=1,              # Frequency of series
                        d=None,           # Let model determine 'd'
                        seasonal=False,   # No Seasonality
                        start_P=0, 
                        D=0, 
                        trace=True,
                        error_action='ignore',  
                        suppress_warnings=True, 
                        stepwise=True)

    print(model_autoARIMA.summary())
    # model_autoARIMA.plot_diagnostics(figsize=(15,8))


    # Fit the model to all available data (assuming df_log is the entire logged dataset)
    fitted_model = model_autoARIMA.fit(df_log)

    # Define the number of future periods and generate the date range for the forecast
    n_periods = 250
    last_date = df_log.index[-1]
    future_dates = pd.bdate_range(start=last_date + pd.Timedelta(days=1), periods=n_periods, freq='B')

    # Forecast
    fc, conf_int = fitted_model.predict(n_periods=n_periods, return_conf_int=True)

    # Convert the forecast and confidence intervals back to the original scale
    fc_series = np.exp(fc)
    lower_series = np.exp(conf_int[:, 0])
    upper_series = np.exp(conf_int[:, 1])

    # Create the forecast series and align it with the future_dates
    fc_series = fc_series.set_axis(future_dates)
    lower_series = pd.Series(lower_series, index=future_dates)
    upper_series = pd.Series(upper_series, index=future_dates)

    # Plot the forecast with confidence intervals
    plt.figure(figsize=(10,5), dpi=100)
    plt.plot(np.exp(df_log), label='Historical Data')  # Convert the historical data back to the original scale
    plt.plot(fc_series, color='orange', label='Forecasted Stock Price')
    plt.fill_between(lower_series.index, lower_series, upper_series, color='k', alpha=.10)
    plt.title(f'Future Stock Price Prediction for {ticker}')
    plt.xlabel('Time')
    plt.ylabel('Forecasted Stock Price')
    plt.legend(loc='upper left', fontsize=8)

    # Save the figure
    plt.savefig(f"data/predictions/{ticker}_forecast.png")

def get_historical_stock_price(ticker):
    API_KEY = 'QC6PHJMTIZHC8S6B'  # Replace with your actual AlphaVantage API key

    url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol={ticker}&outputsize=full&apikey={API_KEY}'

    response = requests.get(url)
    data = response.json()

    if 'Time Series (Daily)' in data:
        print("Data fetched successfully.")
    else:
        return 0

    time_series_data = data['Time Series (Daily)']

    # Initialize an empty DataFrame with the desired columns
    df = pd.DataFrame(columns=['Date', 'Open', 'High', 'Low', 'Close', 'Adjusted Close', 'Volume'])

    # Create a list to hold row data before converting it to a DataFrame
    rows_list = []

    for date, daily_data in time_series_data.items():
        row = {
            'Date': date,
            'Open': daily_data['1. open'],
            'High': daily_data['2. high'],
            'Low': daily_data['3. low'],
            'Close': daily_data['4. close'],
            'Adjusted Close': daily_data['5. adjusted close'],
            'Volume': daily_data['6. volume']
        }
        rows_list.append(row)

    # Convert the list of rows into a DataFrame
    new_df = pd.DataFrame(rows_list)

    # Convert the 'Date' column to datetime and set it as the index
    new_df['Date'] = pd.to_datetime(new_df['Date'])
    new_df.set_index('Date', inplace=True)

    # Sort the DataFrame by the index (Date)
    new_df.sort_index(inplace=True)

    # Filter the DataFrame to the last 3 years
    three_years_ago = datetime.now() - timedelta(days=5*365)
    filtered_df = new_df[new_df.index >= three_years_ago]

    # Save the filtered DataFrame to a CSV file for future use
    filtered_df.to_csv('data/historical_stock_price/' + ticker + '.csv')

    return 1


def main():
    # Read the S&P 500 tickers into a DataFrame
    sp500_df = pd.read_csv('data/SP_500.csv')
    sp500_df = sp500_df[149:]

    # Ensure the 'data/historical_stock_price' and 'data/predictions' directories exist
    os.makedirs('data/historical_stock_price', exist_ok=True)
    os.makedirs('data/predictions', exist_ok=True)

    # Iterate over each ticker in the "Symbol" column
    for ticker in sp500_df['Symbol']:
        print(f"Processing {ticker}")
        result = get_historical_stock_price(ticker)
        if result == 1:
            predict_stock_price(ticker)

# Run the main function
if __name__ == "__main__":
    main()