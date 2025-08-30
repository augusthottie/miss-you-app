import firebase_admin
import os
from firebase_admin import credentials, messaging  # pyright: ignore[reportMissingImports]

# Initialize Firebase with credentials from environment
cred = None
firebase_initialized = False

try:
    if os.getenv('GOOGLE_APPLICATION_CREDENTIALS'):
        # Use service account file path from environment
        cred_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
        cred = credentials.Certificate(cred_path)
        print("Firebase initialized with GOOGLE_APPLICATION_CREDENTIALS")
    elif os.getenv('FIREBASE_SERVICE_ACCOUNT_KEY'):
        # Use service account key JSON from environment variable
        import json
        firebase_key = os.getenv('FIREBASE_SERVICE_ACCOUNT_KEY')
        service_account_info = json.loads(firebase_key)
        cred = credentials.Certificate(service_account_info)
        print("Firebase initialized with FIREBASE_SERVICE_ACCOUNT_KEY")
    else:
        # Try to use default credentials (for local development)
        try:
            cred = credentials.ApplicationDefault()
            print("Firebase initialized with Application Default Credential")
        except Exception as e:
            print(f"Firebase not initialized: {e}")
            print("Push notifications will not work without Firebase")
            firebase_initialized = True  # Mark as handled

    if not firebase_initialized:
        firebase_admin.initialize_app(cred)
        firebase_initialized = True
        print("Firebase initialization successful")

except Exception as e:
    print(f"Firebase initialization failed: {e}")
    print("Push notifications will not work")
    firebase_initialized = True  # Mark as handled


def send_fcm_notification(device_token, title, description, data=None):
    """Send notification using Firebase Cloud Messaging"""
    if not firebase_initialized:
        print("Firebase not initialized, cannot send push notification")
        return False

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
        print(f"Successfully sent push notification: {response}")
        return True

    except Exception as e:
        print(f"Error sending FCM notification: {e}")
        return False
