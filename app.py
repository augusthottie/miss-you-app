from flask import Flask, request, jsonify
from db import (
    init_db,
    notify,
    register,
    register_device_token,
    get_all_users,
    exists,
    mark_as_read,
    get_notifications
)
from dotenv import load_dotenv
from ai import generate_notify_message
import os

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Configure app for production
app.config['JSON_SORT_KEYS'] = False
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False


# Add security headers
@app.after_request
def add_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = \
        'max-age=31536000; includeSubDomains'
    return response


@app.route("/health")
def health_check():
    """Health check endpoint for load balancers"""
    return jsonify({"status": "healthy", "service": "miss-you-app"}), 200


@app.route("/register", methods=["GET"])
def register_endpoint():
    username = request.args.get("username")
    device_token = request.args.get("device_token")

    if not username:
        return jsonify({"error": "Username is required"}), 400

    user_id = register(username)
    if device_token:
        register_device_token(user_id, device_token)

    return jsonify({"user_id": user_id}), 200


@app.route("/exists", methods=["GET"])
def exists_endpoint():
    username = request.args.get("username")

    if not username:
        return jsonify({"error": "Username is required"}), 400

    if_exists = exists(username)
    return jsonify({"exists": if_exists}), 200


@app.route("/notify", methods=["POST"])
def notify_endpoint():
    data = request.get_json()

    if not data:
        return jsonify({"error": "Data is required"}), 400

    if not data.get("source_id"):
        return jsonify({"error": "Source ID is required"}), 400

    if not data.get("target_id"):
        return jsonify({"error": "Target ID is required"}), 400

    title = None
    description = None

    if not data.get("title") or not data.get("description"):
        title, description = generate_notify_message(
            data["source_id"], data["target_id"]
        )
    else:
        title = data["title"]
        description = data["description"]

    success = notify(data["source_id"], data["target_id"], title, description)

    return jsonify({"success": success}), 200


@app.route("/mark_as_read", methods=["GET"])
def mark_as_read_endpoint():
    notification_id = request.args.get("notification_id")

    if not notification_id:
        return jsonify({"error": "Notification ID is required"}), 400

    success = mark_as_read(notification_id)
    return jsonify({"success": success}), 200


@app.route("/users", methods=["POST"])
def users_endpoint():
    get_users = get_all_users()
    return jsonify({"users": get_users}), 200


@app.route("/notifications", methods=["POST"])
def notifications_endpoint():
    data = request.get_json()

    if not data:
        return jsonify({"error": "Data is required"}), 400

    if not data.get("user_id"):
        return jsonify({"error": "User ID is required"}), 400

    notifications = get_notifications(data["user_id"])
    return jsonify({"notifications": notifications}), 200


# Error handlers
@app.errorhandler(404)
def not_found(_):
    return jsonify({"error": "Endpoint not found"}), 404


@app.errorhandler(500)
def internal_error(_):
    return jsonify({"error": "Internal server error"}), 500


if __name__ == "__main__":
    # Initialize database
    init_db()

    # Get port from environment or default to 8000
    port = int(os.getenv('PORT', 8000))

    # Run in production mode
    app.run(host='0.0.0.0', port=port, debug=False)
