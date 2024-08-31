import json
import uuid
from pprint import pprint
from flask import Flask, request, jsonify
from graph import run_graph
from schema_manager import SchemaManager
from history_manager import HistoryManager
from flask_cors import CORS
from rag_graph import update_vectorstore

app = Flask(__name__)
CORS(app)
schema_manager = SchemaManager()
history_manager = HistoryManager()

@app.route('/', methods=['GET', 'POST'])
def answer_question():
    if request.method == 'GET':
        return jsonify({"message": "Server is running and the endpoint is reachable."}), 200

    # for POST requests
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()
    message_user  = data.get("input", {})
    request_type = data.get("input", {}).get("type", "")
    if request_type == "text":
        input = data.get("input", {}).get("text", {}).get("body", "")
    else:
        input_raw = data.get("input", {}).get(request_type, {})
        input_raw["role"] = "User"
        input_raw["request_type"] = request_type

        input = json.dumps(input_raw)

    conversation_id = data.get("conversation_id", None)
    language = data.get("language", "en")

    # TODO: Investigate how this happened
    if (conversation_id == "undefined"):
        conversation_id = None
    
    if not input:
        return jsonify({"error": "Question is required"}), 400

    if conversation_id:
        schema_data = schema_manager.get_schema(conversation_id)
        # schema_data["general_qna"] = {"context_answers": [], "question": ""}
    else:
        schema_data = {
            "other": None,
            "room_recommendation": None,
            "promos": None,
            "manage_booking": None,
            "email_inquiry" : None,
            "commons": None,
            "cancel_reservation": None,
        }
        schema_data["general_qna"] = {"context_answers": [], "question": ""}
        conversation_id = schema_manager.save_schema(schema_data)
    history_manager.save_message(conversation_id, message_user, "user")
    
    try:
        # TO-DO: input should be: { "type": "text", "text": { "body": "Hi! I want to know your promos" } }
        input_data = {"messages": [input], "schemas": schema_data, "current_schema": "none", "is_complete": False, "request_type": request_type, "message_type" : "actionable", "language": language}
        result = run_graph(input_data, conversation_id)

        def object_to_dict(obj):
            return vars(obj) if obj is not None else None
        
        def object_to_dict_2(obj):
            return obj.to_attribute_dict() if obj is not None else None

        schema_data = {
            # "commons": object_to_dict(getattr(result['schemas'], 'commons', None)),
            "other": object_to_dict(getattr(result['schemas'], 'other', None)),
            "room_recommendation": object_to_dict_2(getattr(result['schemas'], 'room_recommendation', None)),
            "promos": object_to_dict_2(getattr(result['schemas'], 'promos', None)),
            "email_inquiry": object_to_dict_2(getattr(result['schemas'], 'email_inquiry', None)),
            "commons": object_to_dict_2(getattr(result['schemas'], 'commons', None)),
            "general_qna": object_to_dict(getattr(result['schemas'], 'general_qna', None)),
            # "manage_booking": object_to_dict(getattr(result['schemas'], 'manage_booking', None)),
            "cancel_reservation": object_to_dict_2(getattr(result['schemas'], 'cancel_reservation', None))
        }


        # It is assumed that even if the conversation_id initially didn't exist, it has been created above before run_graph is called and therefore should already be defined at this point.
        schema_manager.update_schema(conversation_id, schema_data)
                

        # json_response = json.loads(result['messages'][-1])
        print(f"{type(result['messages'][-1])}, {result['messages'][-1]}")
        message_response = json.loads(result['messages'][-1])
        message_id_response = history_manager.save_message(conversation_id, message_response, "ai")

        parsed_result = {
            "messages": message_response,  # Get the last message
            "language": result.get("language", "en"),
            "conversation_id": conversation_id,
            "message_id" : message_id_response
        }
    
        return jsonify(parsed_result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/feedback', methods=['PUT', 'DELETE'])
def manage_feedback():
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400
    
    data = request.get_json()
    message_id = data.get("message_id", None)
    conversation_id = data.get("conversation_id", None)

    if not conversation_id or not message_id:
        return jsonify({"error": "conversation_id and message_id is required!"}), 400

    feedback = data.get("feedback", None)
    if request.method == 'PUT':
        if not feedback:
            return jsonify({"error": "Feedback data must be provided!"}), 400
    elif request.method == 'DELETE':
        feedback = {}
    try:
        pprint(f"CONVERSATION ID: {conversation_id}")
        pprint(f"MESSAGE ID: {message_id}")
        pprint(f"Feedback Received: {feedback}")

        persisted_feedback = history_manager.update_message_feedback(conversation_id,message_id, feedback)
        return jsonify(persisted_feedback), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

@app.route('/history/<conversation_id>', methods=['GET'])
def get_history(conversation_id):    
    if conversation_id is None or len(conversation_id) == 0:
        return jsonify({"error": "conversation_id must be provided!"}), 400

    try:
        pprint(f"CONVERSATION ID: {conversation_id}")

        messages = history_manager.get_history(conversation_id)
        return jsonify({"history" : messages}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
# Update vectorstore
@app.route('/knowledge', methods=['POST'])
def update_knowledge():
    print("Updating knowledge...")
    if not request.is_json:
        print("Request must be JSON")
        return jsonify({"error": "Request must be JSON"}), 400
    
    data = request.get_json()
    old_knowledge_key = data.get("oldKnowledgeKey", None)
    new_knowledge_key = data.get("newKnowledgeKey", None)
    print(f"Old Knowledge Key: {old_knowledge_key}")
    print(f"New Knowledge Key: {new_knowledge_key}")

    if not old_knowledge_key:
        old_knowledge_key = ""

    if not new_knowledge_key:
        print("Knowledge data must be provided!")
        return jsonify({"error": "Knowledge data must be provided!"}), 400
    
    try:
        if update_vectorstore(old_knowledge_key, new_knowledge_key):
            return jsonify({"message": "Knowledge updated successfully"}), 200
        else:
            return jsonify({"error": "An error occurred while updating knowledge"}), 500
    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({"error": str(e)}), 500