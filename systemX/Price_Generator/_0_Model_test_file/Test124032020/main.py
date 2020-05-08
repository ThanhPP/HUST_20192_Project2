import datetime as dt
import time
import pandas_datareader as pdr
import pandas as pd
import yfinance as yf
import numpy as np
from Test124032020 import sample_slopes
from Test124032020 import support_vector

yf.pdr_override()

# Choose the set of stocks
tickers = ["AAPL", "MSFT", "GOOG", "FB"]

# set the time frame to fetch stock data
start = dt.datetime(2013, 10, 1)
end = dt.datetime(2017, 4, 14)


class Ticker_Data:
    """
    use to store stock data
    """

    def __init__(self, df):
        self.main_df = df

    def append_change_column(self, df, ticker):
        """
        Add new columns : change and close
        to the main dataframe (hold the stock info and the ticker of interest)
        """
        df2 = pd.DataFrame()
        df2['Change'] = np.log(df['Close']) - np.log(df['Close'].shift(1))
        self.main_df[str(ticker) + 'CHG'] = df2['Change']
        self.main_df[str(ticker) + 'CLS'] = df['Close']
        return self.main_df

    def drop_row_with_zeros(self):
        """
        remove the row with zero
        """
        columns = list(self.main_df)
        self.main_df = self.main_df[self.main_df[columns] != 0]

    def drop_row_with_NA(self):
        """
        remove the row with NA
        """
        self.main_df = self.main_df.dropna()

    """
    def backTester(self, df):
    # not sure what this function will do ????
    for x in range(len(df.columns) - 2):
        df['stock' + str(x + 1)]
        df['stock1compair'] = np.where(df['stock' + str(x + 1)].values < df['stock' + str(x)].values and
                                       df['stock' + str(x + 1)].values < df['stock' + str(x + 2)].values, 1, 0)
    return df
    """


def write_feature_and_targets(X, Y):
    with open(
            'D:\\go\\src\\github.com\\THANHPP\\HUST_20192_Project2\\Test124032020\\files\\testing_files\\all_feature'
            '.txt',
            'w'
    ) as file_name:
        for feature in X:
            file_name.write(str(feature) + ',' + '\r\n')
        for target in Y:
            file_name.write(str(feature) + ',' + '\r\n')


def main(batch_size, look_ahead):
    i = 0
    main_df = pd.DataFrame()
    ticker_data = Ticker_Data(main_df)

    for ticker in tickers:
        print(ticker)
        time.sleep(1)

        df = pdr.get_data_yahoo(str(ticker), start=start, end=end)
        df = df.reset_index(level='Date')

        ticker_data.append_change_column(df, ticker)

        i += 50

    ticker_data.main_df.to_csv(
        'before_NA_drop_stock_data_slope_sumNoNA' + str(start.date()) + '--' + str(end.date()) + '.csv', mode="w")

    ticker_data.drop_row_with_NA()
    ticker_data.main_df.to_pickle('stock_data/df_without_NA_' + str(start.date()) + '--' + str(end.date()) + '.pkl')

    # print(pd.read_pickle('D:\\go\\src\\github.com\\THANHPP\\HUST_20192_Project2\\Test124032020\\stock_data\\df_without_NA_2013-10-01--2017-04-14.pkl'))

    print("done")
    time.sleep(1)
    ticker_data.main_df = pd.read_pickle(
        'D:\\go\\src\\github.com\\THANHPP\\HUST_20192_Project2\\Test124032020\\stock_data\\df_without_NA_2013-10-01'
        '--2017-04-14.pkl'
    )

    ticker_data.main_df = sample_slopes.create_slope_sum_market(ticker_data.main_df)
    ticker_data.main_df.to_csv('stock_data_slope_sumNoNA' + str(start.date()) + str(end.date()) + '.csv')

    columns = list(ticker_data.main_df)

    columns_with_sample_slopes = sample_slopes.get_columns_with_slope_sum(columns)

    sv = support_vector.Support_Vector([], [])

    for column in columns_with_sample_slopes:
        y_values = sample_slopes.generate_target_value(
            ticker_data.main_df, batch_size, column.replace('slope_sum', 'CLS'), look_ahead)
        sv.Y = sv.Y + y_values[0]
        # print('sv.Y : ', sv.Y)

        x_values = sample_slopes.create_batch_of_slope(
            ticker_data.main_df, column, batch_size, y_values[1]
        )
        sv.X = sv.X + x_values
        # print('sv.X : ', sv.X)
        print()

    write_feature_and_targets(sv.X, sv.Y)

    # print((sv.Y, 'Yvalues'))
    # print(sv.X[-1], ' Xvalues ')
    print('training the model...')

    sv.train()


main(1, 1)
