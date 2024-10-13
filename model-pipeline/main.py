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
def answer_question():
    # TODO: Investigate best practices for global variables in Flask
    global website_info

    if request.method == 'GET':
        return jsonify({"message": "Server is running and the endpoint is reachable."}), 200

    # for POST requests
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    # Data has 2 fields: doc and imgs
    data = request.get_json()

    if website_info == {} and not data.get('doc'):
        return jsonify({"error": "Field doc required"}), 400

    if not data.get('url') or (not data.get('doc') and not data.get('imgs')):
        return jsonify({"error": "Fields url and doc or img required"}), 400
    
    # If doc is not empty, it means that the whole document is updated
    if data.get('doc'):
        print("Updating the whole document")
        # Update the document
        website_info = parse_document(data.get('doc'))
        print(website_info)
    else:
        print("Updating the images")
        # Update the images
        # TODO: Implement this

    # The 'src' attribute of the image
    image_url = website_info['images'][0]["src"]
    # Relative path handling
    if not image_url.startswith(('http://', 'https://')):
        image_url = urljoin(data.get('url'), image_url)

    sub_images = website_info['images']

    state = {
        "input_image_src": sub_images[0]["src"],
        "input_context": website_info['description'],
        "input_image_attrs": sub_images[0]["attrs"],
        "input_a_button_parent": sub_images[0]["a_button_parent"],
        "input_next_text": sub_images[0]["next_text"],

        "correct_alt_text": sub_images[0]["alt"],

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
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500