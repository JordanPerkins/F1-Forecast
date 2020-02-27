import os
import mysql.connector as mysql
import logging
import sys

SQL_USER = os.getenv('MYSQL_USER')
SQL_PASSWORD = os.getenv('MYSQL_PASSWORD')
SQL_HOST = os.getenv('MYSQL_HOST')
SQL_DATABASE = os.getenv('MYSQL_DB')

def connect():
    try:
        return mysql.connection.MySQLConnection(user=SQL_USER, password=SQL_PASSWORD, host=SQL_HOST, database=SQL_DATABASE)
    except mysql.Error as err:
        logging.error('Could not connect to database: '+str(err))
        sys.exit()

class Database:
    # Here will be the instance stored.
    __instance = None

    @staticmethod
    def get_database():
        """ Static access method. """
        if Database.__instance == None:
            Database()
        return Database.__instance

    def get_race_list():
        cursor = db.cursor()
        query = ("SELECT DISTINCT REPLACE(LOWER(name), ' grand prix', '') FROM races ORDER BY raceId;")
        cursor.execute(query)
        return list(cursor)

    def __init__(self):
        if Database.__instance == None:
            self.db = connect()
            Database.__instance = self
