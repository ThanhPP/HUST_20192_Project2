import datetime as dt
import time

import matplotlib.pyplot as pyplot
import pandas as pd
import pandas_datareader as pdr
import tensorflow as tf
import yfinance as yf
import numpy as np
from sklearn.preprocessing import RobustScaler

from Test042020 import ticker_data as td

# library config
yf.pdr_override()
# pd.set_option('display.max_columns', None)
print(tf.__version__)

# dataset
tickers = ["AAPL", "MSFT"]
start = dt.datetime(2001, 1, 1)
end = dt.datetime(2019, 12, 31)

# flag
readfile_flag = False


def create_dataset(X, y, steps=1):
    Xs, ys = [], []
    for i in range(len(X) - steps):
        v = X.iloc[i: (i + steps)].to_numpy()
        Xs.append(v)
        ys.append(y.iloc[i: i + steps])
    return np.array(Xs), np.array(ys)


def main():
    # GET DATA
    main_df = pd.DataFrame()
    ticker_data = td.Ticker_Data(main_df)

    if not readfile_flag:
        for ticker in tickers:
            print("Crawling : " + ticker)
            time.sleep(1)

            df = pdr.get_data_yahoo(str(ticker), start=start, end=end)
            df = df.reset_index(level='Date')

            ticker_data.append_default_column(df, ticker, 'Close')
            ticker_data.append_default_column(df, ticker, 'Volume')

        ticker_data.main_df.to_csv('csv_files\\stock_data_close_and_volume{0}--{1}.csv'.format(str(start.date()),
                                                                                               str(end.date())),
                                   mode="w")
    else:
        print("Reading data from file")
        ticker_data.main_df = pd.read_csv('csv_files\\stock_data_close_and_volume{0}--{1}.csv'.format(str(start.date()),
                                                                                                      str(end.date())),
                                          index_col=0)

    print(ticker_data.main_df.head())

    # PREPARE THE DATA SET
    # split train and test set 0.9/0.1
    train_size = int(len(ticker_data.main_df) * 0.9)
    test_size = int(len(ticker_data.main_df)) - train_size
    train = ticker_data.main_df.iloc[0:train_size]
    test = ticker_data.main_df.iloc[train_size:len(ticker_data.main_df)]
    print(train.shape, test.shape)



main()
