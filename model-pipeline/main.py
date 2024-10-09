import json
import uuid
from flask import Flask, request, jsonify
from graph import run_graph
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/', methods=['GET', 'POST'])
def answer_question():
    if request.method == 'GET':
        return jsonify({"message": "Server is running and the endpoint is reachable."}), 200

    # for POST requests
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()
    
    try:
        # Generate random thread ID
        data['thread_id'] = str(uuid.uuid4())
        result = run_graph(data, data.get('thread_id'))
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500