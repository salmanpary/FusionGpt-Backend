from flask import Flask, request, jsonify
from dotenv import load_dotenv
import os

# Load environment variables from the .env file
load_dotenv()
app = Flask(__name__)


@app.route("/api/chat-completion/palm2", methods=["POST"])
def get_data():
    try:
        # Get JSON data from the request
        json_data = request.get_json()
        palm2_api_key =os.getenv("google_api_key")
        print(palm2_api_key)
        # check if prompt
        # Todo: Add the palm2 code here
        if "prompt" in json_data:
            # Return the received JSON data in the response
            return jsonify(json_data)
        else:
            # If 'prompt' key is missing, return an error message
            return jsonify({"error": 'Invalid JSON format. Missing "prompt" key.'}), 400

    except Exception as e:
        # Return an error message if any exception occurs
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500


@app.route("/api/chat-completion/gpt", methods=["POST"])
def get_data1():
    try:
        # Get JSON data from the request
        json_data = request.get_json()
        #learn how to use azure open ai
        #integrate the api

        # check if prompt
        # Todo: Add the palm2 code here
        if "prompt" in json_data:
            # Return the received JSON data in the response
            return jsonify(json_data)
        else:
            # If 'prompt' key is missing, return an error message
            return jsonify({"error": 'Invalid JSON format. Missing "prompt" key.'}), 400

    except Exception as e:
        # Return an error message if any exception occurs
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500


@app.route("/api/chat-completion/llama2", methods=["POST"])
def get_data2():
    try:
        # Get JSON data from the request
        json_data = request.get_json()

        # check if prompt
        # Todo: Add the palm2 code here
        if "prompt" in json_data:
            # Return the received JSON data in the response
            return jsonify(json_data)
        else:
            # If 'prompt' key is missing, return an error message
            return jsonify({"error": 'Invalid JSON format. Missing "prompt" key.'}), 400

    except Exception as e:
        # Return an error message if any exception occurs
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500


if __name__ == "__main__":
    app.run(debug=True)
