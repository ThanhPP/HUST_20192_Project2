import mysql.connector
from mysql.connector import Error

# CONFIG
HOST = "127.0.0.1"
PORT = "3306"
DATABASE = "stockdata"
USER = "root"
PASSWORD = "Thanh.1809PP"


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
        host=HOST,
        port=PORT,
        database=DATABASE,
        usr=USER,
        pwd=PASSWORD
    )

    cursor = connection.cursor()

    mySQL_query = "SELECT *" \
                  "FROM " + str(ticker)

    cursor.execute(mySQL_query)

    records = cursor.fetchall()

    print(f"Total rows = {cursor.rowcount}")

    close_connection(connection)


get_stock_data("GOOG")


