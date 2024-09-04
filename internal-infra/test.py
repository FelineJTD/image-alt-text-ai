import json
import uuid
from pprint import pprint
from graph import run_graph
from load_data import load_data
import os
# from rag_graph import update_vectorstore

def generate_alt_text(data):
    try:
        # Generate random thread ID
        data['thread_id'] = str(uuid.uuid4())
        result = run_graph(data, data.get('thread_id'))
        return result
    except Exception as e:
        return str(e)


# Main
if __name__ == "__main__":
    json_dir = "../scraper/output"

    correct_roles = 0
    incorrect_roles = 0

    # Loop through each JSON file in the directory
    for filename in os.listdir(json_dir):
        if filename.endswith(".json"):
            try:
                # Read the JSON file
                with open(os.path.join(json_dir, filename), "r") as file:
                    data = json.load(file)
                
                # Extract the image link and textual context from the JSON data
                whole_text = data["text"]
                sub_images = data["images"]

                # for image in sub_images[0]:
                final_state = generate_alt_text({
                    "input_image_src": sub_images[0]["src"],
                    "input_image_filename": sub_images[0]["file_name"],
                    "input_context": whole_text,
                    "input_image_attrs": sub_images[0]["attrs"],
                    "input_a_button_parent": sub_images[0]["a_button_parent"],
                    "input_previous_text": sub_images[0]["previous_text"],
                    "input_next_text": sub_images[0]["next_text"],

                    "correct_role": sub_images[0]["role"],
                    "correct_alt_text": sub_images[0]["alt"],

                    "ai_predicted_role": "",
                    "ai_predicted_alt_text": "",
                })

                if final_state["ai_predicted_role"] == sub_images[0]["role"]:
                    correct_roles += 1
                else:
                    incorrect_roles += 1
            except Exception as e:
                print(str(e))

    pprint(f"Correct roles: {correct_roles}")
    pprint(f"Incorrect roles: {incorrect_roles}")

    pprint(f"Accuracy: {correct_roles / (correct_roles + incorrect_roles)}")