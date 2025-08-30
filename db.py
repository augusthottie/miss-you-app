import os
import psycopg
from contextlib import contextmanager
from dotenv import load_dotenv
from firebase import send_fcm_notification

# Load environment variables
load_dotenv()

# Database configuration
DATABASE_URL = os.getenv('DATABASE_URL')

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is required")


@contextmanager
def get_db_connection():
    """Context manager for PostgreSQL database connections"""
    conn = None
    try:
        conn = psycopg.connect(DATABASE_URL)
        # Return dict-like cursor for easier data access
        with conn.cursor(row_factory=psycopg.rows.dict_row) as cursor:
            yield cursor
    except Exception as e:
        if conn:
            conn.rollback()
        raise e
    finally:
        if conn:
            conn.close()


def init_db():
    """Initialize the database by executing SQL from init.sql file"""
    sql_path = os.path.join(os.path.dirname(__file__), 'queries', 'init.sql')

    conn = psycopg.connect(DATABASE_URL)
    try:
        with open(sql_path, 'r') as f:
            sql_script = f.read()

        with conn.cursor() as cursor:
            cursor.execute(sql_script)
        conn.commit()
        print("Database initialized successfully")
    except Exception as e:
        conn.rollback()
        print(f"Database initialization failed: {e}")
        raise e
    finally:
        conn.close()


def register(username):
    conn = psycopg.connect(DATABASE_URL)
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                'INSERT INTO users (username) VALUES (%s) RETURNING id',
                (username,)
            )
            result = cursor.fetchone()
            conn.commit()
            return result['id'] if result else None
    except Exception as e:
        conn.rollback()
        print(f"Error registering user: {e}")
        raise e
    finally:
        conn.close()


def exists(username):
    conn = psycopg.connect(DATABASE_URL)
    try:
        with conn.cursor() as cursor:
            cursor.execute('SELECT id FROM users WHERE username = %s', (username,))
            result = cursor.fetchone()
            return result is not None
    except Exception as e:
        print(f"Error checking user existence: {e}")
        return False
    finally:
        conn.close()


def register_device_token(user_id, device_token):
    """Register a device token for a user"""
    conn = psycopg.connect(DATABASE_URL)
    try:
        with conn.cursor() as cursor:
            # Remove any existing tokens for this user (optional - you might want
            # to keep multiple devices)
            cursor.execute(
                'DELETE FROM user_devices WHERE user_id = %s', (user_id,))
            # Add the new token
            cursor.execute(
                'INSERT INTO user_devices (user_id, device_token) VALUES (%s, %s)',
                (user_id, device_token))
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"Error registering device token: {e}")
        raise e
    finally:
        conn.close()


def get_user_device_tokens(user_id):
    """Get all device tokens for a user"""
    conn = psycopg.connect(DATABASE_URL)
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                'SELECT device_token FROM user_devices WHERE user_id = %s',
                (user_id,))
            results = cursor.fetchall()
            return [row['device_token'] for row in results]
    except Exception as e:
        print(f"Error getting device tokens: {e}")
        return []
    finally:
        conn.close()


def get_user(username):
    """Get a user by username"""
    conn = psycopg.connect(DATABASE_URL)
    try:
        with conn.cursor() as cursor:
            cursor.execute('SELECT id FROM users WHERE username = %s', (username,))
            result = cursor.fetchone()
            return result['id'] if result else None
    except Exception as e:
        print(f"Error getting user: {e}")
        return None
    finally:
        conn.close()


def notify(source_id, target_id, title, description):
    """Send notification to a user"""
    conn = psycopg.connect(DATABASE_URL)
    try:
        # Get the target user's device tokens
        device_tokens = get_user_device_tokens(target_id)

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
            if send_fcm_notification(
                device_token,
                title,
                description,
                notification_data
            ):
                success_count += 1

        # Insert notification into database
        with conn.cursor() as cursor:
            cursor.execute(
                'INSERT INTO notifications '
                '(source_id, target_id, title, description) '
                'VALUES (%s, %s, %s, %s)',
                (source_id, target_id, title, description)
            )
        conn.commit()

        print(f"📱 Sent {success_count} notifications successfully")
        return success_count > 0

    except Exception as e:
        conn.rollback()
        print(f"Error sending notification: {e}")
        return False
    finally:
        conn.close()


def mark_as_read(notification_id):
    """Mark a notification as read"""
    conn = psycopg.connect(DATABASE_URL)
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                'UPDATE notifications SET is_read = TRUE WHERE id = %s',
                (notification_id,)
            )
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        conn.rollback()
        print(f"Error marking notification as read: {e}")
        return False
    finally:
        conn.close()


def get_all_users():
    """Get all users"""
    conn = psycopg.connect(DATABASE_URL)
    try:
        with conn.cursor() as cursor:
            cursor.execute('SELECT id, username FROM users')
            results = cursor.fetchall()
            return [(row['id'], row['username']) for row in results]
    except Exception as e:
        print(f"Error getting all users: {e}")
        return []
    finally:
        conn.close()


def get_notifications(user_id):
    """Get all notifications for a user"""
    conn = psycopg.connect(DATABASE_URL)
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                'SELECT id, title, description, created_at, is_read '
                'FROM notifications WHERE target_id = %s AND is_read = FALSE',
                (user_id,)
            )
            results = cursor.fetchall()
            return [(row['id'], row['title'], row['description'],
                    str(row['created_at']), row['is_read']) for row in results]
    except Exception as e:
        print(f"Error getting notifications: {e}")
        return []
    finally:
        conn.close()
