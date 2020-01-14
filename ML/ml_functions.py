import pandas as pd
import requests
import os
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
import numpy as np
from statsmodels.tsa.statespace.sarimax import SARIMAX
from scipy.stats import boxcox
from scipy.special import inv_boxcox
import warnings
warnings.filterwarnings("ignore")



def get_historical_data(ticker, days_previous):
    
    url = "https://min-api.cryptocompare.com/data/v2/histoday"
    key = os.getenv("cryptocompare_key")
    payload = {
    "api_key": key,
    "fsym": ticker,
    "tsym": "USD",
    "limit": days_previous
    }
    result = requests.get(url, params = payload).json()
    coin_df = pd.DataFrame(result['Data']['Data'])
    coin_df['time'] = pd.to_datetime(coin_df['time'], unit = 's')
    coin_df = coin_df[['close', 'time']]
    coin_df = coin_df.rename(columns = {'time': 'Date'})
    coin_df = coin_df.set_index('Date')
    return coin_df

def get_arima_forecast(ticker):
    days_previous_dict = {'BTC': 730, 'ETH': 365, 'LTC': 365}
    days_previous = days_previous_dict[ticker]
    coin_df = get_historical_data(ticker, days_previous)
    transformed_data, lmda = boxcox(coin_df)
    transformed_data = transformed_data.flatten().tolist()
    transformed_df = coin_df.copy()
    transformed_df['close'] = transformed_data
    if ticker == 'BTC':
        model = SARIMAX(transformed_df, order = ((0,0,0,0,0,0,0,0,1,0,0,0,0,1),1,(1,0,1,1,1)))
    elif ticker == 'ETH':
        model = SARIMAX(transformed_df, order = ((1,0,0,1),2,1))
    else:
        model = SARIMAX(transformed_df, order = ((0,0,0,0,0,0,0,0,1),1,(0,0,0,0,0,0,0,0,0,1)))

    model_fit = model.fit(disp = False)
    conf_int = model_fit.get_forecast(5)
    confidence_intervals = conf_int.conf_int()
    confidence_intervals = inv_boxcox(confidence_intervals, lmda)
    start = days_previous + 1
    end = days_previous + 6
    predictions = model_fit.predict(start= start, end = end)
    predicted_close = inv_boxcox(predictions, lmda)
    final_df = confidence_intervals.copy()
    final_df['predicted_close'] = predicted_close
    final_df = final_df.round(2)
    return final_df

def get_arima_forecast_plot(ticker):
    forecast_df = get_arima_forecast(ticker)
    plt.style.use('dark_background')
    fig = plt.figure(figsize = (15,8))
    plt.plot(forecast_df['predicted_close'], marker = 'o', color = 'y')
    plt.fill_between(forecast_df.index, forecast_df['lower close'],forecast_df['upper close'], color = 'b', alpha = 0.6)
    plt.ylabel('Price')
    plt.xlabel('Date')
    plt.margins(0.02)
    plt.xticks(forecast_df.index)
    for i,j in zip(forecast_df.index[0:4], forecast_df['predicted_close'][0:4]):
        plt.annotate(str(j),xy=(i,j), xytext = (10,5), textcoords= 'offset points')
    return fig
    
    
    