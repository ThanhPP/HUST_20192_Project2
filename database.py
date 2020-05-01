import mysql.connector
from mysql.connector import Error
from mysql.connector import errorcode


def connect(host, database, usr, pwd):
    print(f"Connecting to {host}")
    try:
        connection = mysql.connector.connect(
            host=host,
            database=database,
            user=usr,
            password=pwd
        )
        return connection
    except mysql.connector.Error as error:
        print(f"Failed to create connection to db : {error}")
        return


def close_connection(connection):
    if connection.is_connected():
        connection.close()
        print(f"Connection closed")
        return

    print("Connection is not connected")
    return


def get_stock_data(connection):
    cursor = connection.cursor()

    mySQL_query = ""
    cursor.execute(mySQL_query)

    records = cursor.fetchall()
    print(f"Total rows = {cursor.rowcount}")



