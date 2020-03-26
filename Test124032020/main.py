import datetime as dt
import pandas_datareader as pdr
import yfinance as yf


# set the time frame to fetch stock data
start = dt.datetime(2013, 10, 1)
end = dt.datetime(2017, 4, 14)

# choose the stock
ticker = 'FB'

# get the data
fbTk = yf.Ticker(ticker)
fbTk.info

# get historical info
historyData = fbTk.history(start=start, end=end)
print(historyData)
