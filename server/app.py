from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_migrate import Migrate

from models import db, Message

app = Flask(__name__)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

# Initialize CORS and database migration
CORS(app)
migrate = Migrate(app, db)
db.init_app(app)

@app.route('/messages', methods=['GET', 'POST'])
def messages():
    # GET: Return all messages
    if request.method == 'GET':
        messages = Message.query.order_by(Message.created_at).all()
        return jsonify([message.to_dict() for message in messages]), 200

    # POST: Create a new message
    elif request.method == 'POST':
        data = request.get_json()
        if not data.get("body") or not data.get("username"):
            return jsonify({"error": "Invalid input"}), 400

        new_message = Message(
            body=data["body"],
            username=data["username"]
        )
        db.session.add(new_message)
        db.session.commit()
        return jsonify(new_message.to_dict()), 201

@app.route('/messages/<int:id>', methods=['GET', 'PATCH', 'DELETE'])
def messages_by_id(id):
    # Fetch message using `Session.get()` instead of `Query.get()`
    message = db.session.get(Message, id)
    
    if not message:
        return jsonify({"error": "Message not found"}), 404

    # GET: Return the specific message
    if request.method == 'GET':
        return jsonify(message.to_dict()), 200

    # PATCH: Update the message body
    elif request.method == 'PATCH':
        data = request.get_json()
        if not data.get("body"):
            return jsonify({"error": "Invalid input"}), 400

        message.body = data["body"]
        db.session.commit()
        return jsonify(message.to_dict()), 200

    # DELETE: Remove the message
    elif request.method == 'DELETE':
        db.session.delete(message)
        db.session.commit()
        return jsonify({"message": "Message deleted"}), 200

if __name__ == '__main__':
    app.run(port=5555)
