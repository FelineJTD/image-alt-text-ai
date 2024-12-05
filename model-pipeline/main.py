import uuid
import json
from flask import Flask, request, jsonify
from graph import run_graph
from flask_cors import CORS
from utils import parse_document
from urllib.parse import urljoin

app = Flask(__name__)
CORS(app)

# # Global variables
# website_info = {}

# @app.route('/', methods=['GET', 'POST'])
# def generate_alt_text():
#     # TODO: Investigate best practices for global variables in Flask
#     global website_info

#     if request.method == 'GET':
#         return jsonify({"message": "Server is running and the endpoint is reachable."}), 200

#     # for POST requests
#     if not request.is_json:
#         return jsonify({"error": "Request must be JSON"}), 400

#     # Get the JSON data
#     data = request.get_json()

#     # If the website information is not provided, return an error
#     if (website_info == {} and not data.get('data')) or not data.get('url'):
#         return jsonify({"error": "Field data and url required"}), 400
    
#     # Parse the document and get the website information
#     website_info = data.get('data')
#     print(website_info)

#     # Initialize the results list
#     results = []

#     # Loop through each image
#     for img in website_info['images']:

#         # The 'src' attribute of the image
#         image_url = img["src"]
#         # Relative path handling
#         if not image_url.startswith(('http://', 'https://')):
#             image_url = urljoin(data.get('url'), image_url)

#         state = {
#             "input_image_src": image_url,
#             "input_context": website_info['description'],
#             "input_image_attrs": img["attrs"],
#             "input_a_button_parent": img["a_button_parent"],
#             "input_next_text": img["next_text"],

#             "correct_role": "",
#             "correct_alt_text": img["alt"],

#             "ai_predicted_role": "",
#             "ai_summarized_context": "",
#             "ai_extracted_text": "",
#             "ai_extracted_entities": {},
#             "ai_predicted_alt_text": "",
#         }
        
#         # Generate alt texts for each images
#         try:
#             # Generate random thread ID
#             data['thread_id'] = str(uuid.uuid4())
#             result = run_graph(state, data.get('thread_id'))
#             print(result['ai_predicted_alt_text'])
#             results.append(result['ai_predicted_alt_text'])
#         except Exception as e:
#             return jsonify({"error": str(e)}), 500
        
#     return jsonify(results), 200

@app.route('/', methods=['GET', 'POST'])
def generate_alt_text():
    if request.method == 'GET':
        return jsonify({"message": "Server is running and the endpoint is reachable."}), 200

    # for POST requests
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    # Get the JSON data
    data = request.get_json()

    # body = {
    #     docUrl mandatory,
    #     docTitle optional,
    #     docDescription optional,
    #     docText optional,
    #     imgSrc mandatory,
    #     imgAlt optional,
    #     imgAttrs optional,
    #     imgAnchorOrButtonParent optional,
    #     imgPrevText optional,
    #     imgNextText optional,
    # }

    print(data)

    # If any mandatory info is missing, return an error
    if (not data.get('docUrl') or not data.get('imgSrc')):
        return jsonify({"error": "Fields docUrl and imgSrc required"}), 400

    doc_url = data.get('docUrl')
    doc_title = data.get('docTitle') if data.get('docTitle') else ""
    doc_description = data.get('docDescription') if data.get('docDescription') else ""
    doc_text = data.get('docText') if data.get('docText') else ""
    img_src = data.get('imgSrc')
    img_alt = data.get('imgAlt') if data.get('imgAlt') else ""
    img_attrs = json.dumps(data.get('imgAttrs')) if data.get('imgAttrs') else ""
    img_a_button_parent = data.get('imgAnchorOrButtonParent') if data.get('imgAnchorOrButtonParent') else "None"
    img_prev_text = data.get('imgPrevText') if data.get('imgPrevText') else ""
    img_next_text = data.get('imgNextText') if data.get('imgNextText') else ""

    # Relative path handling
    if not img_src.startswith(('http://', 'https://')):
        img_src = urljoin(data.get('url'), img_src)

    # TODO
    state = {
        "input_doc_url": doc_url,
        "input_doc_title": doc_title,
        "input_doc_description": doc_description,
        "input_doc_text": doc_text,
        "input_img_src": img_src,
        "input_img_attrs": img_attrs,
        "input_img_a_button_parent": img_a_button_parent,
        "input_img_prev_text": img_prev_text,
        "input_img_next_text": img_next_text,

        "correct_role": "",
        "correct_alt_text": img_alt,

        "ai_predicted_role": "",
        "ai_summarized_context": "",
        "ai_extracted_text": "",
        "ai_extracted_entities": "",
        "ai_predicted_contextual_alt_text": "",
        "ai_predicted_contextual_alt_text_confidence": 0.0,
        "ai_predicted_descriptive_alt_text": "",
    }
    
    # Generate alt texts for each images
    try:
        # Generate random thread ID
        data['thread_id'] = str(uuid.uuid4())
        result = run_graph(state, data.get('thread_id'))
        print(result['ai_predicted_contextual_alt_text'])
        return jsonify({"contextualAltText": result['ai_predicted_contextual_alt_text'], "contextualAltTextConfidence" : result['ai_predicted_contextual_alt_text_confidence'], "descriptiveAltText": result['ai_predicted_descriptive_alt_text'], "humanAltText": result['correct_alt_text']}), 200
    except Exception as e:
        print(str(e))
        return jsonify({"error": str(e)}), 500
        