import mysql.connector
import pandas as pd
from mysql.connector import Error
import config
import datetime


def connect():
    # print(f"Connecting to {config.getEnvValue('HOST')}")
    try:
        connection = mysql.connector.connect(
            host=config.getEnvValue("HOST"),
            port=config.getEnvValue("PORT"),
            database=config.getEnvValue("DATABASE"),
            user=config.getEnvValue("USER"),
            password=config.getEnvValue("PASSWORD"),
        )
        return connection
    except Error as error:
        print("Failed to create connection to db : {error}")
        return


def close_connection(connection):
    if connection.is_connected():
        connection.close()
        print("Connection closed")
        return

    print("Connection is not connected")
    return


def get_stock_data(ticker):
    connection = connect()

    if check_ticker_db(ticker, connection) != "ok":
        return pd.DataFrame()

    df = pd.read_sql('SELECT * FROM ' + ticker
                     + ' WHERE `timestamp` '
                       'BETWEEN \'' + config.getEnvValue("START_DATE") + ' 00:00:00 AM\' ' +
                     'AND \'' + config.getEnvValue("END_DATE") + ' 00:00:00 AM\';'
                     , con=connection)

    # close_connection(connection)

    return df


def get_stock_list():
    connection = connect()
    stock_list = []
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM ticker')
    for row in cursor:
        if (row[1] == "ok") & (row[0] not in stock_list):
            stock_list.append(row[0])

    # close_connection(connection)
    return stock_list


def check_ticker_db(ticker, connection):
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM ticker WHERE name LIKE "' + ticker + '" LIMIT 1;')
    # close_connection(connection)
    for row in cursor:
        return row[1]


def push_predicted_to_db(input_ticker, input_price, input_mse, input_mae, input_accuracy):
    ticker = str(input_ticker)
    price = str("%12.6f" % input_price)
    timestamp = str(datetime.datetime.now())
    mse = str("%.3f" % input_mse)
    mae = str("%.3f" % input_mae)
    accuracy = str("%.3f" % input_accuracy)
    """
    sql = "INSERT INTO `predicted` (ticker, price, timestamp,mse, mae, accuracy) VALUES (%s, %s, %s, %s, %s);"
    val = (str(ticker), str(price), timestamp, str(mse), str(mae), str(accuracy))
    try:
        connection = connect()
        cursor = connection.cursor()
        cursor.execute('UPDATE `predicted`'
                       ' SET `price`= "' + price + '",' +
                       '`timestamp`= "' + timestamp + '",' +
                       '`mse`= "' + mse + '",' +
                       '`mae`=  "' + mae + '",' +
                       '`accuracy` = "' + accuracy + '"' +
                       ' WHERE `ticker` LIKE "' + ticker + '";')
        connection.commit()
    except Error:
    """
    connection = connect()
    cursor = connection.cursor()
    sql = "INSERT INTO `predicted` (ticker, price, timestamp,mse, mae, accuracy) VALUES (%s, %s, %s,%s, %s, %s);"
    val = (str(ticker), str(price), str(timestamp), str(mse), str(mae), str(accuracy))
    cursor.execute(sql, val)
    connection.commit()
    # close_connection(connection)


# print(get_stock_data("GOOG").head())
"""
print('INSERT INTO `predicted` (`ticker`, `predicted_price`, `mse`, `mae`, `accuracy`) ' +
      'VALUES (`' + 'ticker' + '`,`' + 'price' + '`,`' + 'mse' + '`,`' + 'mae' + '`,`' + 'accuracy' + '`)')

print('UPDATE `predicted`'
      ' SET `predicted_price`= "' + "price" + '",' +
      '`mse`= "' + "mse" + '",' +
      '`mae`=  "' + "mae" + '",' +
      '`accuracy` = "' + "accuracy" + '"' +
      ' WHERE `ticker` LIKE "' + "ticker" + '";')

print(get_stock_list())

print(check_ticker_db("GOOG", connect()))

print(get_stock_data("GOOG"))
"""

