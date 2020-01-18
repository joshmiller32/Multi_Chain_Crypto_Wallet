import pandas as pd
import requests
import os
import numpy as np
from statsmodels.tsa.statespace.sarimax import SARIMAX
from scipy.stats import boxcox
from scipy.special import inv_boxcox
import plotly.express as px
from plotly.io import write_html
from datetime import datetime
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
    coin_df = coin_df.rename(columns = {'time': 'Date'}).set_index('Date')
    return coin_df

def get_arima_forecast(ticker):
    days_previous_dict = {'BTC': 730, 'ETH': 730, 'LTC': 730}
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
    final_df['Predicted Price'] = predicted_close
    final_df = final_df.round(2)
    final_df = final_df.reset_index()
    final_df = final_df.rename(columns = {'index': 'Date'})
    return final_df

def get_arima_forecast_plot():
    ticker_list = ['BTC', 'ETH', 'LTC']
    for ticker in ticker_list:
        forecast_df = get_arima_forecast(ticker)
        fig = px.linefig = px.line(forecast_df, x ='Date', y = 'Predicted Price')
        fig.update_xaxes(nticks = 5)
        fig.update_yaxes(automargin=True)
        fig.update_layout(title_text = f'{ticker} Arima Model', autosize = True, height = 800, width = 950, template = 'seaborn')
        write_html(fig, f'./web/{ticker}Arima.html')

    
    