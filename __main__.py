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

load_dotenv()

app = Flask(__name__)


@app.route("/register", methods=["GET"])
def register_endpoint():
    username = request.args.get("username")
    device_token = request.args.get("device_token")

    if not username:
        return jsonify({"error": "Username is required"}), 400

    user_id = register(username)
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


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
