import sqlite3
from contextlib import contextmanager
import os
from firebase import send_fcm_notification

DATABASE_FILE_PATH = "database.db"


@contextmanager
def get_db_connection():
    """Context manager for database connections"""
    conn = sqlite3.connect(DATABASE_FILE_PATH)
    try:
        yield conn
    finally:
        conn.close()


def init_db():
    """Initialize the database by executing SQL from init.sql file"""
    sql_path = os.path.join(os.path.dirname(__file__), 'queries', 'init.sql')
    with get_db_connection() as conn:
        with open(sql_path, 'rb') as f:
            conn.executescript(f.read().decode('utf8'))
        conn.commit()


def register(username):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO users (username) VALUES (?)', (username,))
        conn.commit()
        return cursor.lastrowid


def exists(username):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
        return cursor.fetchone() is not None


def register_device_token(user_id, device_token):
    """Register a device token for a user"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        # Remove any existing tokens for this user (optional - you might want
        # to keep multiple devices)
        cursor.execute(
            'DELETE FROM user_devices WHERE user_id = ?', (user_id,))
        # Add the new token
        cursor.execute(
            'INSERT INTO user_devices (user_id, device_token) VALUES (?, ?)',
            (user_id, device_token))
        conn.commit()


def get_user_device_tokens(user_id):
    """Get all device tokens for a user"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            'SELECT device_token FROM user_devices WHERE user_id = ?',
            (user_id,))
        return [row[0] for row in cursor.fetchall()]


def get_user(username):
    """Get a user by username"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
        return cursor.fetchone()


def notify(source_id, target_id, title, description):
    """Send notification to a user"""

    # Get user
    source_user = get_user(source_id)[0]

    # Get the target user's device tokens
    device_tokens = get_user_device_tokens(source_user)

    if not device_tokens:
        print(f"No device tokens found for user {target_id}")
        return False

    # Prepare notification data
    notification_data = {
       "source_user_id": str(source_id),
       "target_user_id": str(target_id),
       "type": "miss_you_notification"
    }

    # Send to all user's devices
    success_count = 0
    for device_token in device_tokens:
        send_fcm_notification(
            device_token,
            title,
            description,
            notification_data
        )

        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO notifications '
                '(source_id, target_id, title, description) '
                'VALUES (?, ?, ?, ?)',
                (source_id, target_id, title, description)
            )
            conn.commit()

        success_count += 1

    return success_count > 0


def mark_as_read(notification_id):
    """Mark a notification as read"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE notifications SET is_read = TRUE WHERE id = ?', (
                notification_id,
            )
        )

        conn.commit()
        return cursor.rowcount > 0


def get_all_users():
    """Get all users"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT id, username FROM users')
        return cursor.fetchall()


def get_notifications(user_id):
    """Get all notifications for a user"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            'SELECT id, title, description, created_at, is_read '
            'FROM notifications WHERE target_id = ? AND is_read = FALSE',
            (user_id,)
        )
        return cursor.fetchall()
