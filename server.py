from flask import Flask, request, jsonify
from dotenv import load_dotenv
import hashlib
import os
import jwt
from openai import OpenAI
from db import mydb,cursor
from flask_cors import CORS

load_dotenv()

jwt_secret = os.getenv('jwt_secret')
openai_api_key = os.getenv('openai_api_key')


# Function to hash a password using SHA-256
def hash_password(password):
    password_bytes = password.encode('utf-8')
    hashed_password = hashlib.sha256(password_bytes).hexdigest()
    return hashed_password


def verify_user(email, password):
    select_user_sql = "SELECT id, username, email, password FROM users WHERE email = %s"
    cursor.execute(select_user_sql, (email,))
    user = cursor.fetchone()
    if user:
        id, username, stored_email, stored_password = user
        if stored_password == hash_password(password):
            return id, username, stored_email, True
    return None, None, None, False

# Function to decode and verify JWT token
def decode_jwt_token(token):
    try:
        decoded_token = jwt.decode(token, jwt_secret, algorithms=['HS256'])
        return decoded_token
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

# Initialize Flask app
app = Flask(__name__)
CORS(app)
@app.route('/auth/signup', methods=['POST'])
def register_user():
    # Get data from request
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    hashed_password = hash_password(password)

    # Insert user data into database
    insert_user_sql = "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)"
    user_data = (username, email, hashed_password)
    cursor.execute(insert_user_sql, user_data)
    mydb.commit()

    return jsonify({'message': 'User registered successfully'}), 201

# Endpoint to handle user login
@app.route('/auth/login', methods=['POST'])
def login_user():
    # Get data from request
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    # Verify user credentials
    id, username, user_email, authenticated = verify_user(email, password)
    
    if authenticated:
        # Generate JWT token
        token_payload = {
            'id': id,
            'username': username,
            'user_email': user_email,
            'authenticated': authenticated
        }
        token = jwt.encode(token_payload, jwt_secret, algorithm='HS256')
        return jsonify({'token': token})
    else:
        return jsonify({'message': 'Invalid email or password'}), 401


# Endpoint to get all users if authenticated
@app.route('/users', methods=['GET'])
def get_all_users():
    # Get JWT token from request headers
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'message': 'No token provided'}), 401

    # Decode and verify JWT token
    decoded_token = decode_jwt_token(token)
    print(decoded_token)
    if not decoded_token:
        return jsonify({'message': 'Invalid token'}), 401

    # Get all users from the database
    select_all_users_sql = "SELECT * FROM users"
    cursor.execute(select_all_users_sql)
    users = cursor.fetchall()

    # Convert users to a list of dictionaries
    users_list = []
    for user in users:
        user_dict = {
            'id': user[0],
            'username': user[1],
            'email': user[2]
        }
        users_list.append(user_dict)

    return jsonify({'users': users_list}), 200
@app.route("/chat/getmessage/openai", methods=["GET"])
def get_user_chat_history():
    # Get JWT token from request headers
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'message': 'No token provided'}), 401

    # Decode and verify JWT token
    decoded_token = decode_jwt_token(token)
    if not decoded_token:
        return jsonify({'message': 'Invalid token'}), 401

    # Extract user ID from decoded token
    user_id = decoded_token.get('id')

    # Fetch model ID from the models table (assuming the model ID is stored in the decoded token)
    model_id = decoded_token.get('model_id')

    # Query the chat_history table for messages associated with the user ID and model ID, sorted by timestamp
    select_user_chat_history_sql = """
    SELECT * FROM chat_history 
    WHERE user_id = %s AND model_id = %s 
    ORDER BY timestamp ASC
    """
    cursor.execute(select_user_chat_history_sql, (user_id, model_id))
    user_chat_history = cursor.fetchall()

    # Convert chat history to a list of dictionaries
    chat_history_list = []
    for message in user_chat_history:
        message_dict = {
            'id': message[0],
            'user_id': message[1],
            'model_id': message[2],
            'query': message[3],
            'answer': message[4],
            'timestamp': message[5].isoformat()  # Convert timestamp to ISO format for JSON serialization
        }
        chat_history_list.append(message_dict)

    return jsonify({'chat_history': chat_history_list}), 200

    
    
@app.route('/chat/openai', methods=['POST'])
def openai_chat():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'message': 'No token provided'}), 401
    decoded_token = decode_jwt_token(token)
    if not decoded_token:
        return jsonify({'message': 'Invalid token'}), 401
    
    data = request.get_json()
    messages = data.get('messages')
    
    model="gpt-3.5-turbo"
    client = OpenAI(
        api_key=openai_api_key
    )
    response = client.chat.completions.create(
    model=model,
    messages=messages,
    temperature=0,
    )
    query = messages[len(messages)-1]['content']
    response= response.choices[0].message
    insert_chat_history_sql = """
    insert into chat_history (user_id, model_id, query, answer) values (%s, %s, %s, %s)
    """
    cursor.execute(insert_chat_history_sql, (decoded_token.get('id'), 1, query, response.content))
    messages.append({
        'role': 'system',
        'content': response.choices[0].message.content
    })
    return jsonify(messages)
if __name__ == "__main__":
    app.run(debug=True)
