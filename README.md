# Miss You App

A Flask-based backend application for sending personalized "miss you" notifications with AI-generated messages using Google's Gemini AI and Firebase Cloud Messaging for push notifications.

## Features

- 🤖 **AI-Generated Messages**: Uses Google Gemini AI to create personalized, heartfelt messages
- 📱 **Push Notifications**: Firebase Cloud Messaging integration for iOS/Android notifications
- 👥 **User Management**: Register users and manage device tokens
- 💾 **SQLite Database**: Lightweight database for storing users, notifications, and device tokens
- 🔔 **Notification System**: Send, receive, and mark notifications as read

## Tech Stack

- **Backend**: Flask (Python)
- **Database**: SQLite
- **AI**: Google Gemini AI
- **Push Notifications**: Firebase Cloud Messaging
- **Environment Management**: python-dotenv
- **Production Server**: Gunicorn (WSGI)
- **Reverse Proxy**: Nginx
- **Containerization**: Docker & Docker Compose

## Prerequisites

- Python 3.8+ (for development)
- Docker & Docker Compose (for production deployment)
- Google Gemini API key
- Firebase project with service account key
- iOS/Android app for receiving notifications

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/augusthottie/miss-you-app
   cd miss-you-app
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file in the root directory:
   ```env
   GOOGLE_API_KEY=your_gemini_api_key_here
   FIREBASE_SERVICE_ACCOUNT_PATH=serviceAccountKey.json
   ```

5. **Set up Firebase**
   - Download your Firebase service account key from Firebase Console
   - Place it in the root directory as `serviceAccountKey.json`
   - Add it to `.gitignore` for security

6. **Initialize the database**
   ```bash
   python __main__.py
   ```

## API Endpoints

### User Management

#### Register User
```http
GET /register?username=<username>&device_token=<device_token>
```
**Response:**
```json
{
  "user_id": 1
}
```

#### Check User Exists
```http
GET /exists?username=<username>
```
**Response:**
```json
{
  "exists": true
}
```

#### Get All Users
```http
POST /users
```
**Response:**
```json
{
  "users": [
    [1, "john_doe"],
    [2, "jane_smith"]
  ]
}
```

### Notifications

#### Send Notification
```http
POST /notify
Content-Type: application/json

{
  "source_id": 1,
  "target_id": 2,
  "title": "Optional custom title",
  "description": "Optional custom description"
}
```
**Response:**
```json
{
  "success": true
}
```

#### Get User Notifications
```http
POST /notifications
Content-Type: application/json

{
  "user_id": 1
}
```
**Response:**
```json
{
  "notifications": [
    [1, "Miss you!", "John is thinking about you", "2024-01-15 10:30:00", false]
  ]
}
```

#### Mark Notification as Read
```http
GET /mark_as_read?notification_id=<id>
```
**Response:**
```json
{
  "success": true
}
```


## Usage Examples

### Using cURL

1. **Register a user:**
   ```bash
   curl "http://localhost:5000/register?username=john_doe&device_token=your_device_token_here"
   ```

2. **Send a notification:**
   ```bash
   curl -X POST http://localhost:5000/notify \
     -H "Content-Type: application/json" \
     -d '{"source_id": 1, "target_id": 2}'
   ```

3. **Get notifications:**
   ```bash
   curl -X POST http://localhost:5000/notifications \
     -H "Content-Type: application/json" \
     -d '{"user_id": 2}'
   ```

### Using Python

```python
import requests

# Register user
response = requests.get("http://localhost:5000/register", params={
    "username": "john_doe",
    "device_token": "your_device_token"
})
user_id = response.json()["user_id"]

# Send notification
response = requests.post("http://localhost:5000/notify", json={
    "source_id": 1,
    "target_id": user_id
})
```

## API Endpoints

### User Management
- `GET /register?username=<username>&device_token=<token>` - Register a new user
- `GET /exists?username=<username>` - Check if username exists
- `POST /users` - Get all users

### Notifications
- `POST /notify` - Send a notification (supports AI-generated content)
- `POST /notifications` - Get user notifications
- `GET /mark_as_read?notification_id=<id>` - Mark notification as read

### Health Check
- `GET /health` - Application health status

### Request Examples

```bash
# Register user
curl "http://localhost:5000/register?username=john_doe&device_token=your_device_token"

# Send notification
curl -X POST http://localhost:5000/notify \
  -H "Content-Type: application/json" \
  -d '{"source_id": 1, "target_id": 2}'

# Get notifications
curl -X POST http://localhost:5000/notifications \
  -H "Content-Type: application/json" \
  -d '{"user_id": 2}'
```

## AI Message Generation

The app uses Google Gemini AI to generate personalized messages. When no custom title/description is provided, the AI creates:

- **Title**: Short, catchy message (max 30 characters)
- **Description**: Sweet, personal message (max 100 characters)

Example AI-generated messages:
- Title: "Missing your smile ✨"
- Description: "Every day feels brighter when I think of you"

## Push Notifications

The app supports Firebase Cloud Messaging for sending push notifications to iOS and Android devices. Device tokens are stored in the database and used to send notifications.

## Development

### Running the Development Server
```bash
python app.py
```
The server will start on `http://localhost:5000`

### Project Structure
```
miss-you-app/
├── app.py                   # Flask app and API endpoints
├── db.py                    # Database operations
├── ai.py                    # Gemini AI integration
├── firebase.py              # Firebase push notifications
├── requirements.txt         # Python dependencies
├── .env                     # Environment variables
├── serviceAccountKey.json   # Firebase service account
├── Dockerfile               # Docker container configuration
├── docker-compose.yml       # Multi-service deployment
├── gunicorn.conf.py         # Production server configuration
├── nginx.conf               # Reverse proxy configuration
├── queries/
│   └── init.sql            # Database initialization
└── README.md               # This file
```

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GOOGLE_API_KEY` | Google Gemini API key | Yes |
| `FIREBASE_SERVICE_ACCOUNT_PATH` | Path to Firebase service account JSON | Yes |

## Production Deployment

The app includes production-ready deployment configurations for containerized environments.

### Docker Deployment

1. **Prerequisites:**
   - Docker and Docker Compose installed
   - Environment variables set up

2. **Quick Start:**
   ```bash
   # Set environment variables
   export GOOGLE_API_KEY="your_gemini_api_key"
   export FIREBASE_SERVICE_ACCOUNT_KEY='{"type":"service_account",...}'

   # Build and run
   docker-compose up --build -d
   ```

3. **Access your app:**
   - **API**: `http://localhost:8000`
   - **Health Check**: `http://localhost:8000/health`

### Manual Gunicorn Deployment

```bash
# Install dependencies
pip install -r requirements.txt

# Run with Gunicorn
gunicorn --config gunicorn.conf.py app:app
```

### Production Files

- **`Dockerfile`**: Containerized deployment configuration
- **`docker-compose.yml`**: Multi-service deployment with Nginx
- **`gunicorn.conf.py`**: Gunicorn WSGI server configuration
- **`nginx.conf`**: Nginx reverse proxy configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GOOGLE_API_KEY` | Google Gemini API key | Yes |
| `FIREBASE_SERVICE_ACCOUNT_KEY` | Firebase service account JSON | Yes |
| `PORT` | Server port (default: 8000) | No |

## Security Considerations

- Never commit `.env` or `serviceAccountKey.json` to version control
- Use HTTPS in production
- Implement proper authentication and authorization
- Validate all input data
- Use environment variables for sensitive configuration
