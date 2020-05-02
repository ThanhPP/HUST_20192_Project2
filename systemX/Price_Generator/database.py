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

    df = pd.read_sql('SELECT * FROM ' + ticker, con=connection)

    close_connection(connection)

    return df


get_stock_data("GOOG")


