import mysql.connector
from database import cursor, db

COLLECTIONS_DIR = 'collections'


def get_one(collection_id: int) -> dict:
    cursor.execute(f"SELECT * FROM collections WHERE collection_id = {collection_id}")
    return cursor.fetchone()


def get_all() -> list:
    cursor.execute("SELECT * FROM collections")
    return cursor.fetchall()


def insert_one(name: str) -> None:
    try:
        cursor.execute(f"INSERT INTO collections (name) VALUES ('{name}')")
        db.commit()

        print(f"Inserted collection: {name}")
    except mysql.connector.Error as err:
        print(err.msg)
