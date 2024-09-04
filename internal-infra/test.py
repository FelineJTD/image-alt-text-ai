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

    # Loop through each JSON file in the directory
    filename = os.listdir(json_dir)[0]
    if filename.endswith(".json"):
        # Read the JSON file
        with open(os.path.join(json_dir, filename), "r") as file:
            data = json.load(file)
        
        # Extract the image link and textual context from the JSON data
        whole_text = data["text"]
        sub_images = data["images"]

        # for image in sub_images[0]:
        pprint(generate_alt_text({
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
        }))

    # Generate alt text

    # pprint(generate_alt_text(data[0]))
    # pprint(data)
    # Generate alt text
    # for d in data:
    #     pprint(generate_alt_text(d))
    # pprint(generate_alt_text({
    #     "image_src": str,
    #     "image_filename": str,
    #     "alt_text": str,
    #     "role": str,
    #     "context": str,
    #     "image_attrs": dict,
    #     "a_button_parent": str,
    #     "previous_text": str,
    #     "next_text": str
    # }))
    #