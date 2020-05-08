import pandas as pd
import pandas_datareader as pdr
import datetime as dt
import yfinance as yf
import numpy as np

from collections import deque
from sklearn import preprocessing
from sklearn.model_selection import train_test_split

yf.pdr_override()

# dataset
TICKER = "AAPL"
START = dt.datetime(2001, 1, 1)
END = dt.datetime(2019, 12, 31)
FEATURE_COLUMNS = ['Adj Close', 'Volume', 'Open', 'High', 'Low']
LOOKUP_STEPS = 1
N_STEPS = 50
TEST_SIZE = 0.1


def load_data(ticker=TICKER, feature_columns=FEATURE_COLUMNS, lookup_steps=LOOKUP_STEPS, n_steps=N_STEPS,
              test_size=TEST_SIZE):
    result = {}
    # GET STOCK DATA
    print("from ", START, "to ", END)
    print("Crawling : " + str(ticker))
    df = pdr.get_data_yahoo(str(ticker), start=START, end=END)

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
    y = np.array(y)
    # reshape X to fit the neural network
    X = X.reshape((X.shape[0], X.shape[2], X.shape[1]))
    # split the dataset
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size)
    result['X_train'] = X_train
    result['X_test'] = X_test
    result['y_train'] = y_train
    result['y_test'] = y_test

    # RETURN
    return result


load_data()
