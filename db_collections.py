import mysql.connector
from database import cursor, db


def get_all() -> dict:
    cursor.execute("SELECT * FROM collections")
    return cursor.fetchall()


def insert_one(name: str) -> None:
    try:
        cursor.execute(f"INSERT INTO collections (name) VALUES ('{name}')")
        db.commit()

        print(f"Inserted collection: {name}")
    except mysql.connector.Error as err:
        print(err.msg)
