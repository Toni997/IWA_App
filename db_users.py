import mysql.connector
from database import db, cursor

EMAIL_PATTERN = r'^[a-zA-Z0-9.!#$%&’*+/=?^_`{|}~-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*$'
USERNAME_PATTERN = r'^(?=[a-zA-Z0-9._]{3,45}$)(?!.*[_.]{2})[^_.].*[^_.]$'


def get_one(user_id: int) -> dict:
    cursor.execute(f"SELECT * FROM users WHERE user_id = {user_id}")
    return cursor.fetchone()


def get_one_with_email_or_username(email: str, username: str):
    cursor.execute(f"SELECT * FROM users WHERE email = '{email}' OR username = '{username}'")
    return cursor.fetchone()


def get_one_with_username(username: str):
    cursor.execute(f"SELECT * FROM users WHERE username = '{username}'")
    return cursor.fetchone()


def get_one_with_session_hash(session_hash: str):
    cursor.execute(f"""
                    SELECT users.user_id, users.username, users.is_admin, users.salt, users.password_hash
                    FROM users
                    INNER JOIN sessions
                    ON users.user_id = sessions.user_id
                    WHERE session_hash = '{session_hash}'
                    """)
    return cursor.fetchone()


def insert_one(email: str, username: str, salt: str, pw_hash: str) -> None:
    try:
        cursor.execute(
                    f"""
                        INSERT INTO users
                        (
                        email,
                        username,
                        salt,
                        password_hash
                        )
                        VALUES
                        (
                        '{email}',
                        '{username}',
                        '{salt}',
                        '{pw_hash}'
                        )
                    """
                    )
        db.commit()

        print(f"Created user: {username}")
    except mysql.connector.Error as err:
        print(err.msg)


def update_password(user_id: int, salt, pw_hash):
    try:
        cursor.execute(
                    f"""
                    UPDATE users
                    SET salt = '{salt}', password_hash = '{pw_hash}'
                    WHERE user_id = {user_id};
                    """
                    )
        db.commit()

        print(f"Updated user: {user_id}")
    except mysql.connector.Error as err:
        print(err.msg)

