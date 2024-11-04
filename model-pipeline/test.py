import json
import requests
import os
# from main import generate_alt_text
# import uuid
# from graph import run_graph

backend_url = "http://localhost:5000/"

def generate_alt_text_call(data):
    # Send a POST request to the backend
    response = requests.post(backend_url, json=data)
    print(response.json())
    # thread_id = str(uuid.uuid4())
    # result = run_graph(data, thread_id)
    # print(result['ai_predicted_alt_text'])

    # Return the response
    return response


# Main
if __name__ == "__main__":
    json_dir = "../scraper/output"

    correct_roles = 0
    incorrect_roles = 0

    # Loop through each JSON file in the directory
    for filename in os.listdir(json_dir)[0:1]:
        if filename.endswith(".json"):
            try:
                # Read the JSON file
                with open(os.path.join(json_dir, filename), "r") as file:
                    data = json.load(file)
                
                # Extract the image link and textual context from the JSON data
                whole_text = data["text"]
                sub_images = data["images"]

                # for image in sub_images[0]:
                final_state = generate_alt_text_call({
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
                    "ai_summarized_context": "",
                    "ai_extracted_text": "",
                    "ai_extracted_entities": {},
                    "ai_predicted_alt_text": "",
                })

                if (final_state["ai_predicted_role"]).lower() == sub_images[0]["role"]:
                    correct_roles += 1
                else:
                    incorrect_roles += 1

                # Save the final state to a JSON file
                with open(f"./output/{filename}", "w") as file:
                    json.dump(final_state, file, indent=4)

            except Exception as e:
                print(str(e))

    print(f"Correct roles: {correct_roles}")
    print(f"Incorrect roles: {incorrect_roles}")

    print(f"Accuracy: {correct_roles / (correct_roles + incorrect_roles)}")