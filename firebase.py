import firebase_admin
from firebase_admin import credentials, messaging

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)


def send_fcm_notification(device_token, title, description, data=None):
    """Send notification using Firebase Cloud Messaging"""
    try:
        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=description
            ),
            data=data or {},
            token=device_token
        )

        response = messaging.send(message)
        print(f"Successfully sent message: {response}")
        return True

    except Exception as e:
        print(f"Error sending FCM notification: {e}")
        return False
