#!C:\Users\tkazinoti\AppData\Local\Programs\Python\Python310\python.exe
import mysql.connector
from mysql.connector import errorcode
from database import cursor

DB_NAME = 'iwa'
TABLES = dict()

TABLES['users'] = """
    CREATE TABLE `users` (
      `user_id` int NOT NULL AUTO_INCREMENT,
      `username` varchar(45) NOT NULL,
      `password_hash` binary(60) NOT NULL,
      `is_admin` tinyint(1) NOT NULL DEFAULT 0,
      PRIMARY KEY (`user_id`),
      UNIQUE KEY `username_UNIQUE` (`username`)
    ) ENGINE=InnoDB;
    """

# sessions table
# images table
# collections tables


def create_database():
    cursor.execute(
        f"CREATE DATABASE IF NOT EXISTS {DB_NAME} DEFAULT CHARACTER SET 'utf8"
    )
    print(f"Database created {DB_NAME}.")


def create_tables():
    cursor.execute(f"USE {DB_NAME}")

    for table_name in TABLES:
        create_table_statement = TABLES[table_name]
        try:
            print(f"Attempting to create table {table_name}.")
            cursor.execute(create_table_statement)
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                print(f"Could not create table {table_name}! Table already exists.")
            else:
                print(err.msg)


create_database()
create_tables()
