import mysql.connector
from mysql.connector import errorcode

from database import cursor, DB_NAME

TABLES = dict()
TABLES['users'] = """

    CREATE TABLE `users` (
      `user_id` int NOT NULL AUTO_INCREMENT,
      `email` varchar(320) NOT NULL,
      `username` varchar(45) NOT NULL,
      `salt` char(64) NOT NULL,
      `password_hash` char(64) NOT NULL,
      `is_admin` tinyint(1) NOT NULL DEFAULT '0',
      PRIMARY KEY (`user_id`),
      UNIQUE KEY `username_UNIQUE` (`username`),
      UNIQUE KEY `email_UNIQUE` (`email`)
    ) ENGINE=InnoDB

    """

TABLES['sessions'] = """

    CREATE TABLE `sessions` (
      `session_id` int NOT NULL,
      `user_id` int NOT NULL,
      `valid_until` timestamp NULL DEFAULT NULL,
      PRIMARY KEY (`session_id`),
      KEY `user_id_idx` (`user_id`),
      CONSTRAINT `user_id` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE ON UPDATE RESTRICT
    ) ENGINE=InnoDB

    """

TABLES['collections'] = """

    CREATE TABLE `collections` (
      `collection_id` int NOT NULL AUTO_INCREMENT,
      `name` varchar(45) NOT NULL,
      PRIMARY KEY (`collection_id`),
      UNIQUE KEY `name_UNIQUE` (`name`)
    ) ENGINE=InnoDB;

    """

TABLES['images'] = """

    CREATE TABLE `images` (
      `image_id` int NOT NULL AUTO_INCREMENT,
      `path` varchar(255) NOT NULL,
      `counter` int DEFAULT '0',
      `created` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
      `last_visited` timestamp NULL DEFAULT NULL,
      `collection_id` int NOT NULL,
      PRIMARY KEY (`image_id`),
      KEY `collection_id_idx` (`collection_id`),
      CONSTRAINT `collection_id` FOREIGN KEY (`collection_id`)
      REFERENCES `collections` (`collection_id`) ON DELETE CASCADE ON UPDATE RESTRICT
    ) ENGINE=InnoDB;

    """


def create_database():
    cursor.execute(
        f"CREATE DATABASE IF NOT EXISTS {DB_NAME} DEFAULT CHARACTER SET 'utf8'"
    )
    print(f"Database created {DB_NAME}.")


def create_tables():
    cursor.execute(f"USE {DB_NAME}")

    for table_name in TABLES:
        create_table_statement = TABLES[table_name]
        try:
            print(f"Attempting to create table {table_name}...")
            cursor.execute(create_table_statement)
            print("Table created!")
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                print(f"Could not create table {table_name}! Table already exists.")
            else:
                print(err.msg)


create_database()
create_tables()
