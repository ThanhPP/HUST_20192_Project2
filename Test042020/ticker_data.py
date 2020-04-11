import pandas as pd


class Ticker_Data:
    def __init__(self, df):
        self.main_df = df

    def append_default_column(self, df, ticker, feature):
        df2 = pd.DataFrame()
        self.main_df[str(ticker) + feature] = df[feature]
        return self.main_df
