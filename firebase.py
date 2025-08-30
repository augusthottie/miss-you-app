import firebase_admin
import os
from firebase_admin import credentials, messaging

# Initialize Firebase with credentials from environment
cred = None
if os.getenv('GOOGLE_APPLICATION_CREDENTIALS'):
    # Use service account file path from environment
    cred = credentials.Certificate(os.getenv('GOOGLE_APPLICATION_CREDENTIALS'))
elif os.getenv('FIREBASE_SERVICE_ACCOUNT_KEY'):
    # Use service account key JSON from environment variable
    import json
    service_account_info = json.loads(
        os.getenv('FIREBASE_SERVICE_ACCOUNT_KEY')
    )
    cred = credentials.Certificate(service_account_info)
else:
    # Try to use default credentials (for local development)
    cred = credentials.ApplicationDefault()

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
