import datetime

import mysql.connector
from database import cursor, db

ALLOWED_FILE_TYPES = ['png', 'jpeg']


def get_one(image_id: int) -> dict:
    cursor.execute(f"SELECT * FROM images WHERE image_id = {image_id}")
    return cursor.fetchone()


def get_all() -> list:
    cursor.execute("""
                    SELECT image_id, path, counter, created, last_visited, images.collection_id, name
                    FROM images INNER JOIN collections
                    ON images.collection_id = collections.collection_id
                    """)
    return cursor.fetchall()


def get_all_with_collection_id(collection_id: int) -> list:
    cursor.execute(f"""
                    SELECT image_id, path, created, last_visited, images.collection_id, name
                    FROM images INNER JOIN collections
                    ON images.collection_id = collections.collection_id
                    WHERE images.collection_id = '{collection_id}'
                    """)
    return cursor.fetchall()


def insert_one(path: str, collection_id: int) -> None:
    try:
        cursor.execute(f"""INSERT INTO images (path, collection_id) VALUES ("{path}", '{collection_id}')""")
        db.commit()

        print(f"Inserted image: {path}")
    except mysql.connector.Error as err:
        print(err.msg)


def patch_one(image_id: int, now: str) -> None:
    try:
        cursor.execute(f"UPDATE images SET counter = counter + 1, last_visited = '{now}' WHERE image_id = {image_id}")
        db.commit()

        print(f"Patched image: {image_id}")
    except mysql.connector.Error as err:
        print(err.msg)


def delete_one(image_id: int) -> None:
    try:
        cursor.execute(f"DELETE FROM images WHERE image_id = {image_id}")
        db.commit()

        print(f"Deleted image: {image_id}")
    except mysql.connector.Error as err:
        print(err.msg)
