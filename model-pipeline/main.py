import uuid
from flask import Flask, request, jsonify
from graph import run_graph
from flask_cors import CORS
from utils import parse_document
from urllib.parse import urljoin

app = Flask(__name__)
CORS(app)

# Global variables
website_info = {}

@app.route('/', methods=['GET', 'POST'])
def generate_alt_text():
    # TODO: Investigate best practices for global variables in Flask
    global website_info

    if request.method == 'GET':
        return jsonify({"message": "Server is running and the endpoint is reachable."}), 200

    # for POST requests
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    # Get the JSON data
    data = request.get_json()

    # If the website information is not provided, return an error
    if (website_info == {} and not data.get('doc')) or not data.get('url'):
        return jsonify({"error": "Field doc and url required"}), 400
    
    # Parse the document and get the website information
    website_info = parse_document(data.get('doc'))
    print(website_info)

    # Initialize the results list
    results = []

    # Loop through each image
    for img in website_info['images']:

        # The 'src' attribute of the image
        image_url = img["src"]
        # Relative path handling
        if not image_url.startswith(('http://', 'https://')):
            image_url = urljoin(data.get('url'), image_url)

        state = {
            "input_image_src": image_url,
            "input_context": website_info['description'],
            "input_image_attrs": img["attrs"],
            "input_a_button_parent": img["a_button_parent"],
            "input_next_text": img["next_text"],

            "correct_role": "",
            "correct_alt_text": img["alt"],

            "ai_predicted_role": "",
            "ai_summarized_context": "",
            "ai_extracted_text": "",
            "ai_extracted_entities": {},
            "ai_predicted_alt_text": "",
        }
        
        # Generate alt texts for each images
        try:
            # Generate random thread ID
            data['thread_id'] = str(uuid.uuid4())
            result = run_graph(state, data.get('thread_id'))
            print(result['ai_predicted_alt_text'])
            results.append(result['ai_predicted_alt_text'])
        except Exception as e:
            return jsonify({"error": str(e)}), 500
        
    return jsonify(results), 200