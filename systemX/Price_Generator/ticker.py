import pandas as pd
import pandas_datareader as pdr
import datetime as dt
import yfinance as yf
import numpy as np
import os

import database as db

from collections import deque
from sklearn import preprocessing

yf.pdr_override()

# default dataset
TICKER = "AAPL"
START = dt.datetime(2001, 1, 1)
END = dt.datetime(2019, 12, 31)
FEATURE_COLUMNS = ['open', 'high', 'low', 'close', 'volume']
LOOKUP_STEPS = 1
N_STEPS = 50
TEST_SIZE = 0.1


def check_features_col(df, feature_columns=FEATURE_COLUMNS):
    # make sure that the feature_columns exist in the dataframe
    for col in feature_columns:
        assert col in df.columns


def get_stock_data_from_Yahoo(ticker=TICKER, start=START, end=END):
    print("crawling data of {ticker} from {start} to {end}")
    ticker_data_file_name = "ticker_data/" + ticker + "-" + str(START.date()) + "-" + str(END.date()) + ".csv"

    df = pdr.get_data_yahoo(str(ticker),
                            start=start,
                            end=end)

    print(df.head())

    check_features_col(df)

    df.to_csv(ticker_data_file_name, mode="w")
    return df


def get_stock_data_from_file(ticker=TICKER, start=START, end=END):
    ticker_data_file_name = "ticker_data/" + ticker + "-" + str(start.date()) + "-" + str(end.date()) + ".csv"
    print("Read from file : {ticker_data_file_name}")

    if os.path.isfile(ticker_data_file_name):
        print("File exist -> reading")
        df = pd.read_csv(ticker_data_file_name)

        check_features_col(df)

        return df

    print("{ticker_data_file_name} not exist")
    return pd.DataFrame()


def scale_data(df, feature_columns=FEATURE_COLUMNS):
    column_scaler = {}
    for column in feature_columns:
        scaler = preprocessing.MinMaxScaler()
        df[column] = scaler.fit_transform(np.expand_dims(df[column].values, axis=1))
        column_scaler[column] = scaler

    return column_scaler, df


def generate_future_col(df, feature_col="close", lookup_steps=LOOKUP_STEPS):
    # add the target column (label) by shifting by `lookup_steps`
    # last `lookup_step` columns contains NaN in future column
    df["future"] = df[feature_col].shift(-lookup_steps)
    return df


def generate_sequence_data(df, feature_columns=FEATURE_COLUMNS, lookup_steps=LOOKUP_STEPS, n_steps=N_STEPS):
    # this last_sequence will be used to predict in future dates that are not available in the data set
    last_sequence = np.array(df[feature_columns].tail(lookup_steps))
    df.dropna(inplace=True)

    sequence_data = []
    sequences = deque(maxlen=n_steps)
    for entry, target in zip(df[feature_columns].values, df["future"].values):
        sequences.append(entry)
        if len(sequences) == n_steps:
            sequence_data.append([np.array(sequences), target])

    last_sequence = list(sequences) + list(last_sequence)
    last_sequence = np.array(pd.DataFrame(last_sequence).shift(-1).dropna())

    return sequence_data, last_sequence


def generate_x_and_y(sequence_data, test_size=TEST_SIZE):
    X, y = [], []
    for seq, target in sequence_data:
        X.append(seq)
        y.append(target)

    # convert to numpy array
    X = np.array(X)
    y = np.array(y)

    # reshape X for the model
    X = X.reshape((X.shape[0], X.shape[2], X.shape[1]))

    # split the data
    X_train = X[:int(len(X) * (1 - test_size))]
    y_train = y[:int(len(X) * (1 - test_size))]

    X_test = X[-int(len(y) * test_size):]
    y_test = y[-int(len(y) * test_size):]

    return X_train, y_train, X_test, y_test


def load_data(ticker=TICKER, start=START, end=END, feature_columns=FEATURE_COLUMNS,
              lookup_steps=LOOKUP_STEPS, n_steps=N_STEPS, test_size=TEST_SIZE):
    result = {}

    # get data
    df = pd.DataFrame()
    df = db.get_stock_data(ticker)
    if df.empty:
        return

    result['df'] = df.copy()

    result['column_scaler'], scaled_df = scale_data(df)

    scaled_df = generate_future_col(scaled_df)

    sequence_data, last_sequence = generate_sequence_data(scaled_df, feature_columns=feature_columns,
                                                          lookup_steps=lookup_steps, n_steps=n_steps)

    result['last_sequence'] = last_sequence

    X_train, y_train, X_test, y_test = generate_x_and_y(sequence_data, test_size=test_size)

    result['X_train'] = X_train
    result['y_train'] = y_train
    result['X_test'] = X_test
    result['y_test'] = y_test

    return result


# load_data("GOOG")

""" OLD LOAD_DATA
def load_data(ticker=TICKER, feature_columns=FEATURE_COLUMNS, lookup_steps=LOOKUP_STEPS, n_steps=N_STEPS,
              test_size=TEST_SIZE):
    result = {}

    # GET STOCK DATA
    print("from ", START, "to ", END)
    ticker_data_file_name = "ticker_data/" + ticker + "-" + str(START.date()) + "-" + str(END.date()) + ".csv"

    df = pd.DataFrame()
    if os.path.isfile(ticker_data_file_name):
        print("read from file")
        df = pd.read_csv(ticker_data_file_name)
        # print(df.shape)
        # print(df.head())
    else:
        print("Crawling : " + str(ticker))
        df = pdr.get_data_yahoo(str(ticker), start=START, end=END)
        # print(df.shape)
        # print(df.head())
        df.to_csv(ticker_data_file_name, mode="w")

    # insert df in return
    result['df'] = df.copy()

    # make sure that the feature_columns exist in the dataframe
    for col in feature_columns:
        assert col in df.columns
    # print(df.head())

    # SCALE THE DATA
    column_scaler = {}
    for column in feature_columns:
        scaler = preprocessing.MinMaxScaler()
        df[column] = scaler.fit_transform(np.expand_dims(df[column].values, axis=1))
        column_scaler[column] = scaler

    # insert scaler in return
    result['column_scaler'] = column_scaler
    # print(np.squeeze(column_scaler["Adj Close"].inverse_transform(np.expand_dims(df["Adj Close"].values, axis=1))))
    # add the target column (label) by shifting by `lookup_steps`
    # last `lookup_step` columns contains NaN in future column
    df['future'] = df['Adj Close'].shift(-lookup_steps)
    last_sequence = np.array(df[feature_columns].tail(lookup_steps))
    df.dropna(inplace=True)

    sequence_data = []
    sequences = deque(maxlen=n_steps)
    for entry, target in zip(df[feature_columns].values, df['future'].values):
        sequences.append(entry)
        if len(sequences) == n_steps:
            sequence_data.append([np.array(sequences), target])

    # this last_sequence will be used to predict in future dates that are not available in the data set
    last_sequence = list(sequences) + list(last_sequence)
    last_sequence = np.array(pd.DataFrame(last_sequence).shift(-1).dropna())
    # add to return
    result['last_sequence'] = last_sequence
    # print("last_sequence", last_sequence.shape)

    # CONSTRUCT X & y
    X, y = [], []
    for seq, target in sequence_data:
        X.append(seq)
        y.append(target)
    # convert to numpy arrays
    X = np.array(X)
    # print(X.shape)
    y = np.array(y)
    # reshape X to fit the neural network
    X = X.reshape((X.shape[0], X.shape[2], X.shape[1]))
    # print(X.shape)
    # split the dataset

    X_train = X[:int(len(X) * (1 - test_size))]
    y_train = y[:int(len(X) * (1 - test_size))]
    X_test = X[-int(len(y) * test_size):]
    y_test = y[-int(len(y) * test_size):]

    # X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size)
    result['X_train'] = X_train
    result['y_train'] = y_train

    result['X_test'] = X_test
    result['y_test'] = y_test

    # print(np.squeeze(column_scaler["Adj Close"].inverse_transform(np.expand_dims(y_train, axis=1))))

    # RETURN
    return result
    """
