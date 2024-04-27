from flask import Flask, request, jsonify
from dotenv import load_dotenv
import hashlib
import os
import jwt
from openai import OpenAI
from db import mydb,cursor
from flask_cors import CORS
import google.generativeai as genai
import replicate
import requests
from index_pdf_document import index_pdf_documents,get_db

load_dotenv()

jwt_secret = os.getenv('jwt_secret')
openai_api_key = os.getenv('openai_api_key')
google_api_key = os.getenv('google_api_key')
replicate_api_token = os.getenv('replicate_api_token')
bart_api_token=os.getenv('bart_api_token')
stable_diffusion_url=os.getenv('stable_diffusion_url')
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
@app.route('/getuser', methods=['GET'])
def get_user():
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

    # Fetch user's name from the database based on user ID
    select_user_name_sql = "SELECT username FROM users WHERE id = %s"
    cursor.execute(select_user_name_sql, (user_id,))
    user_name_result = cursor.fetchone()

    if not user_name_result:
        return jsonify({'message': 'User not found'}), 404

    user_name = user_name_result[0]

    return jsonify({'user_name': user_name}), 200


def get_chat_history(user_id, model_id):
    # Query the chat_history table for messages associated with the user ID and model ID, sorted by timestamp
    select_user_chat_history_sql = """
    SELECT query, answer FROM chat_history 
    WHERE user_id = %s AND model_id = %s 
    ORDER BY timestamp ASC
    """
    cursor.execute(select_user_chat_history_sql, (user_id, model_id))
    user_chat_history = cursor.fetchall()

    # Convert chat history to a list of dictionaries
    chat_history_list = []
    for message in user_chat_history:
        message_dict1 = {
            'role': 'user',
            'content': message[0],
        }
        message_dict2 = {
            'role': 'assistant',
            'content': message[1],
        }
        chat_history_list.append(message_dict1)
        chat_history_list.append(message_dict2)

    return chat_history_list

@app.route("/chat/getmessages", methods=["GET"])
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

    # Get the AI model name from the query parameters
    ai_model = request.args.get('model_name')
    if not ai_model:
        return jsonify({'message': 'AI model name is required as query parameter'}), 400

    # Fetch model ID from the models table based on the model name
    select_model_id_sql = "SELECT id FROM model WHERE model_name = %s"
    cursor.execute(select_model_id_sql, (ai_model,))
    model_id_result = cursor.fetchone()

    if not model_id_result:
        return jsonify({'message': f'Model "{ai_model}" not found'}), 404

    model_id = model_id_result[0]

    # Get chat history for the user and model
    chat_history = get_chat_history(user_id, model_id)

    return jsonify({'messages': chat_history}), 200


@app.route('/chat', methods=['POST'])
def openai_chat():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'message': 'No token provided'}), 401
    decoded_token = decode_jwt_token(token)
    if not decoded_token:
        return jsonify({'message': 'Invalid token'}), 401
    
    data = request.get_json()
    messages = data.get('messages')
    model_name = data.get('model_name')  # Get the model name from the request JSON
    print(model_name)
    if not model_name:
        return jsonify({'message': 'Model name is required'}), 400
    
    # Use the provided model name to fetch the model ID from the database
    select_model_id_sql = "SELECT id FROM model WHERE model_name = %s"
    cursor.execute(select_model_id_sql, (model_name,))
    model_id_result = cursor.fetchone()

    if not model_id_result:
        return jsonify({'message': f'Model "{model_name}" not found'}), 404

    model_id = model_id_result[0]
    if model_name == "openai":
    # Use the provided model name for OpenAI chat
        client = OpenAI(
            api_key=openai_api_key
        )
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # Use the provided model name here
            messages=messages,
            temperature=0,
        )
        
        query = messages[-1]['content']  # Assuming the last message is the user's query
        response_content = response.choices[0].message.content
    elif model_name == "palm2":
        genai.configure(api_key=google_api_key)
        model = genai.GenerativeModel(model_name="gemini-pro",)
        print(model)
        query = messages[-1]['content']
        response = model.generate_content(query)
        response_content = response.text
    elif model_name == "llama2":
        os.environ["REPLICATE_API_TOKEN"] = replicate_api_token
        query = messages[-1]['content']
        output = replicate.run(
            "meta/llama-2-70b-chat:02e509c789964a7ea8736978a43525956ef40397be9033abf9fd2badfe68c9e3",
            input={
                "prompt":query
            }
        )
        
        # Collecting output from the iterator
        output_text = "".join([item for item in output])
        response_content = output_text
    elif model_name=="bart":
        query=messages[-1]['content']
        api_url="https://api-inference.huggingface.co/models/facebook/bart-large-cnn"
        headers={"Authorization":f"Bearer {bart_api_token}"}
        payload={"inputs":query}
        response=requests.post(api_url,headers=headers,json=payload)
        response_content=str(response.json()[0]["summary_text"])
        
        
        
        
        
    
    # Insert the chat history into the database
    insert_chat_history_sql = """
    INSERT INTO chat_history (user_id, model_id, query, answer) VALUES (%s, %s, %s, %s)
    """
    cursor.execute(insert_chat_history_sql, (decoded_token.get('id'), model_id, query, response_content))
    mydb.commit()
    
    # Get chat history for the user and model
    chat_history = get_chat_history(decoded_token.get('id'), model_id)
    
    return jsonify({'messages': chat_history}), 200
    # Get data from request
@app.route('/generate-images', methods=['POST'])
def generate_images():
    # Get JWT token from request headers
    # token = request.headers.get('Authorization')
    # if not token:
    #     return jsonify({'message': 'No token provided'}), 401

    # # Decode and verify JWT token
    # decoded_token = decode_jwt_token(token)
    # if not decoded_token:
    #     return jsonify({'message': 'Invalid token'}), 401

    # Get data from request
    data = request.get_json()
    prompt = data.get('prompt')
    steps = 20
    negative_prompt = data.get('negative_prompt')
    batch_size = 2

    # Validate required parameters
    if not all([prompt, steps, negative_prompt, batch_size]):
        return jsonify({'error': 'Missing required parameters'}), 400

    # Call the external API to generate images
    url = stable_diffusion_url
    payload = {
        "prompt": prompt,
        "steps": steps,
        "negative_prompt": negative_prompt,
        "batch_size": batch_size,
    }

    try:
        response = requests.post(url=url, json=payload)
        if response.status_code == 200:
            images = response.json().get("images", [])
            return jsonify({'images': images}), 200
        else:
            print(f"Failed to generate images: {response.text}")
            return jsonify({'error': 'Failed to generate images'}), response.status_code
    except requests.exceptions.RequestException as e:
        print(f"Error generating images: {e}")
        return jsonify({'error': 'Failed to generate images'}), 500


@app.route('/save-documents', methods=['POST'])
def save_documents():
    # Check if request contains files
    UPLOAD_DIRECTORY = "uploads"

    # Ensure the upload directory exists
    if not os.path.exists(UPLOAD_DIRECTORY):
        os.makedirs(UPLOAD_DIRECTORY)
        
    # Check if session ID is provided in the request body
    session_id = request.form.get('sessionId')
    if not session_id:
        return jsonify({'error': 'Session ID is missing in the request body'}), 400

    if 'files[]' not in request.files:
        return jsonify({'error': 'No files found in request'}), 400
    
    # Get the files
    files = request.files.getlist('files[]')

    # Iterate over the files
    saved_files = []
    file_names = []
    for file in files:
        # Check if the file has a valid filename
        if file.filename == '':
            continue
        
        # Save the file to the upload directory
        file_path = os.path.join(UPLOAD_DIRECTORY, file.filename)
        file.save(file_path)
        
        # Append the file path to the response
        saved_files.append(file_path)
        file_names.append(file.filename)
    print(file_names)
    # Call the function with session ID and PDF file names
    index_pdf_documents(session_id, file_names)
    return jsonify({'message': 'Files saved successfully', 'files': saved_files}), 200
@app.route('/chat-with-ktu',methods=['POST'])
def chat_with_ktu():
    data=request.get_json()
    session_id=data.get('session_id')
    query=data.get('query')
    print(session_id)
    print(query)
    db=get_db(session_id)
    matches=db.similarity_search(query,k=5)
    client = OpenAI(
            api_key=openai_api_key
        )
    extra_context=""
    for index,match in enumerate(matches):
        extra_context+=f"Context {index+1}: {match.page_content}\n"
    full_prompt=f"""
    ---
    question from user:
    ---
    {query}
    ---
    context:
    ---
    {extra_context}
    """   
    messages = [
        {
            "role":"system",
            "content": "You will be given context from the top 5 most relevant pages from a document. specified after context: ,always use the context given to answer the question."
        },
        {"role": "user", "content": full_prompt},
    ]
    response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # Use the provided model name here
            messages=messages,
            temperature=0,
        )
        
    return response.choices[0].message.content
if __name__ == "__main__":
    app.run(debug=True)
