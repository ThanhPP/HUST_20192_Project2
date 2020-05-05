import mysql.connector
import pandas as pd
from mysql.connector import Error
import config


def connect(host, port, database, usr, pwd):
    print(f"Connecting to {host}")
    try:
        connection = mysql.connector.connect(
            host=host,
            port=port,
            database=database,
            user=usr,
            password=pwd
        )
        return connection
    except Error as error:
        print(f"Failed to create connection to db : {error}")
        return


def close_connection(connection):
    if connection.is_connected():
        connection.close()
        print(f"Connection closed")
        return

    print("Connection is not connected")
    return


def get_stock_data(ticker):
    connection = connect(
        host=config.getEnvValue("HOST"),
        port=config.getEnvValue("PORT"),
        database=config.getEnvValue("DATABASE"),
        usr=config.getEnvValue("USER"),
        pwd=config.getEnvValue("PASSWORD")
    )

    if check_ticker_db(ticker, connection) != "ok":
        return pd.DataFrame()

    df = pd.read_sql('SELECT * FROM ' + ticker
                     + ' WHERE `timestamp` '
                       'BETWEEN \'' + config.getEnvValue("START_DATE") + ' 00:00:00 AM\' ' +
                     'AND \'' + config.getEnvValue("END_DATE") + ' 00:00:00 AM\';'
                     , con=connection)

    close_connection(connection)

    return df


def check_ticker_db(ticker, connection):
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM ticker WHERE name LIKE \'' + ticker + "\' LIMIT 1;")
    for row in cursor:
        return row[1]


print(get_stock_data("GOOG").head())


