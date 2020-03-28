import numpy as np
import pandas as pd


def create_slope_sum_market(df):
    columns = df.columns
    CLS_columns, CHG_columns = get_columns_with_CLS(columns)
    column_index = 1
    print(CHG_columns)

    while column_index < (len(CHG_columns) - 1):
        stock_looking_at = CHG_columns[column_index]
        slope_sum = pd.DataFrame(np.zeros((len(df.index), 1)))

        for stock in CHG_columns:
            if stock != stock_looking_at:
                slope_sum[0] = slope_sum[0] + df[CHG_columns[column_index]] - df[stock]

        df[str(CHG_columns[column_index].replace('CHG', 'slope_sum'))] = slope_sum

        column_index += 1

    return df


def get_columns_with_CLS(columns):
    """
    Takes an array of columns and returns the ones with CLS at the end
    """
    columns_with_CLS = []
    CHG_columns = []

    for column in columns:
        if column[-3:] == 'CLS':
            columns_with_CLS.append(column)
        else:
            CHG_columns.append(column)

    return columns_with_CLS, CHG_columns


def get_columns_with_slope_sum(columns):
    """
    Takes an array of columns and returns the ones with slope_sum at the end
    """
    columns_with_slope_sum = []
    for column in columns:
        # look at the last 9 characters
        if column[-9:] == 'slope_sum':
            columns_with_slope_sum.append(column)
    return columns_with_slope_sum
