import mysql.connector
from database import cursor, db


def get_session_with_user(session_hash: str):
    cursor.execute(f"""
                    SELECT users.user_id, users.username, users.is_admin, sessions.session_hash, sessions.valid_until
                    FROM sessions
                    INNER JOIN users
                    ON sessions.user_id = users.user_id
                    WHERE session_hash = '{session_hash}'
                    """)
    return cursor.fetchone()


def insert_one(session_hash: str, user_id: int, valid_until: str) -> None:
    try:
        cursor.execute(f"""
                        INSERT INTO sessions
                        (`session_hash`,
                        `user_id`,
                        `valid_until`)
                        VALUES
                        ('{session_hash}',
                        '{user_id}',
                        '{valid_until}');
                        """)
        db.commit()

        print(f"Inserted session: {session_hash}")
    except mysql.connector.Error as err:
        print(err.msg)


def delete_one(session_hash: str) -> None:
    try:
        cursor.execute(f"""
                        DELETE FROM sessions
                        WHERE session_hash = '{session_hash}'
                        """)
        db.commit()

        print(f"Deleted session: {session_hash}")
    except mysql.connector.Error as err:
        print(err.msg)
