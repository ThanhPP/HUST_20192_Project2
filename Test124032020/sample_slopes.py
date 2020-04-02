import numpy as np
import pandas as pd


def create_slope_sum_market(df):
    """
    Takes a dataframe and looks at all the columns with percent change. Then it compare the stock of interest and
    calculates the differences between it and the rest of the percent changes on that day in the market. Finally it sums
    them up. returns the original dataframe with the new columns called Slope_sum
    """

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
                # print(slope_sum[0], '  ', df[CHG_columns[column_index]], '  ', df[stock])

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


def generate_target_value(df, batch_count, column_name, look_ahead):
    """
    Takes a df and a batch count to generate the % change values good or bad for each batch
    """
    list_of_closes = df[column_name].tolist()
    i = 0
    target_values = []

    while i < (len(list_of_closes) - (look_ahead + batch_count) + 1):
        target_day_index = i + batch_count + look_ahead - 1
        percent_change = find_percent_change(list_of_closes[target_day_index], list_of_closes[i + batch_count - 1])
        # print(target_day_index, '  target_day_index  ', list_of_closes[target_day_index])
        if percent_change < 0:
            target_values.append(-1)
        else:
            target_values.append(1)
        i += 1

    number_of_target_values = len(target_values)

    return target_values, number_of_target_values


def find_percent_change(new_number, old_number):
    """
    percent change of 2 numbers
    """
    return (float(new_number) - float(old_number))/float(old_number)


def _sliding_windows(sequence, winSize, step = 1):
    """
    Returns a generator that will iterate through
    the defined chunks of input sequence.
    Input sequence must be iterable.
    """
    # compute the number of chunks
    numOfChunks = ((len(sequence) - winSize)/step) + 1

    for i in range(0, int(numOfChunks) * step, step):
        yield sequence[i: i + winSize]


def create_batch_of_slope(df, column_with_slope_sum, batch_count, cut_length):
    """
    Takes a dataframe of closes changes and slopes and create batches of the slopes of the batch_count
    """
    list_of_chunks = list(_sliding_windows(
        df[column_with_slope_sum].tolist(), batch_count
    ))
    #print(list_of_chunks)

    return list_of_chunks[:cut_length]


def moving_average(a, n):
    ret = np.cumsum(a, dtype=float)
    ret[n:] = ret[n:] - ret[:n]
    return ret[n-1:] / n


def create_batch_of_slopes_moving_av(df, column_with_slope_sum, batch_count, cut_length, moving_window):
    """
    Takes a dataframe of closes changes and slopes and creates batches of the slopes of size batch_count
    """

    # take the dataframe makes it a list. Then only takes the front part of
    # it and sends it to the sliding window to get the feature chunks
    list_of_chunks = list(_sliding_windows(
        df[column_with_slope_sum].tolist(), batch_count))

    moving_av_chunks = []
    for chunk in list_of_chunks:
        moving_av_chunks.append(moving_average(chunk, moving_window))

    return moving_av_chunks[:cut_length]