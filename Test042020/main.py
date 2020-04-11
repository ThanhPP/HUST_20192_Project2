import tensorflow as tf
import datetime as dt
import time
import pandas_datareader as pdr
import pandas as pd
import yfinance as yf
from Test042020 import ticker_data as td
import numpy as np

# library config
yf.pdr_override()
# pd.set_option('display.max_columns', None)
print(tf.__version__)

# dataset
tickers = ["AAPL", "MSFT", "GOOG", "FB"]
start = dt.datetime(2013, 10, 1)
end = dt.datetime(2017, 4, 14)

# flag
readfile_flag = True


def main():
    # get data
    main_df = pd.DataFrame()
    ticker_data = td.Ticker_Data(main_df)

    if not readfile_flag:
        for ticker in tickers:
            print("Crawling : " + ticker)
            time.sleep(1)

            df = pdr.get_data_yahoo(str(ticker), start=start, end=end)
            df = df.reset_index(level="Date")

            ticker_data.append_default_column(df, ticker, 'Close')
            ticker_data.append_default_column(df, ticker, 'Volume')

        ticker_data.main_df.to_csv('csv_files\\stock_data_close_and_volume{0}--{1}.csv'.format(str(start.date()),
                                                                                               str(end.date())),
                                   mode="w")
    else:
        print("Reading data from file")
        ticker_data.main_df = pd.read_csv('csv_files\\stock_data_close_and_volume{0}--{1}.csv'.format(str(start.date()),
                                                                                                      str(end.date())))

    print(ticker_data.main_df.shape)


main()
