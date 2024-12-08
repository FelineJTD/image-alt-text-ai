import json
import requests
import os
# from main import generate_alt_text
import uuid
from graph import run_graph
import random
from bs4 import BeautifulSoup

# backend_url = "http://localhost:5000/"

def generate_alt_text_call(data):
    # Send a POST request to the backend
    # response = requests.post(backend_url, json=data)
    # print(response.json())
    thread_id = str(uuid.uuid4())
    response = run_graph(data, thread_id)
    print(response['ai_predicted_contextual_alt_text'])

    # Return the response
    return response


# Main
if __name__ == "__main__":
    json_dir = "../scraper/output"

    correct_roles = 0
    incorrect_roles = 0

    filenames = os.listdir(json_dir)

    # Shuffle the filenames
    random.seed(42)
    random.shuffle(filenames)

    # Loop through each JSON file in the directory
    for filename in os.listdir(json_dir):
        if filename.endswith(".json") and filename != "output.json":
            try:
                # Read the JSON file
                with open(os.path.join(json_dir, filename), "r") as file:
                    data = json.load(file)
                
                # Extract the image link and textual context from the JSON data
                whole_text = data["text"]
                sub_images = data["images"]

                web_url = filename[:-5]
                # Request and get the doc title and description
                doc_url = f"https://{web_url}"
                doc_title = ""
                doc_description = ""

                try:
                    response = requests.get(doc_url)
                    soup = BeautifulSoup(response.text, "html.parser")
                    doc_title = soup.title.string
                    doc_description = soup.find("meta", {"name": "description"})["content"]

                except Exception as e:
                    print(str(e))

                # Write the doc title and description to the JSON file
                with open(f"../scraper/doc-title-desc/{filename}", "w") as file:
                    json.dump({"doc_title": doc_title, "doc_description": doc_description}, file, indent=4)
                results = []

                for image in sub_images:
                    final_state = generate_alt_text_call({
                        "input_doc_url": filename[:-5],
                        "input_doc_title": doc_title,
                        "input_doc_description": doc_description,
                        "input_doc_text": whole_text,
                        "input_img_src": image["src"],
                        "input_img_attrs": json.dumps(image["attrs"]),
                        "input_img_a_button_parent": image["a_button_parent"],
                        "input_img_prev_text": image["previous_text"],
                        "input_img_next_text": image["next_text"],
                        "input_img_header": "",

                        "correct_role": image["role"],
                        "correct_alt_text": image["alt"],

                        "ai_predicted_role": "",
                        "ai_summarized_context": "",
                        "ai_extracted_text": "",
                        "ai_extracted_entities": "",
                        "ai_predicted_contextual_alt_text": "",
                        "ai_predicted_contextual_alt_text_confidence": 0.0,
                        "ai_predicted_descriptive_alt_text": "",
                    })

                    if (final_state["ai_predicted_role"]).lower() != "":
                        if (final_state["ai_predicted_role"]).lower() == image["role"]:
                            correct_roles += 1
                        else:
                            incorrect_roles += 1

                    results.append(final_state)

                # Save the final state to a JSON file
                with open(f"./output-FINAL/{filename}", "w") as file:
                    json.dump(results, file, indent=4)

            except Exception as e:
                print(str(e))

    print(f"Correct roles: {correct_roles}")
    print(f"Incorrect roles: {incorrect_roles}")

    print(f"Accuracy: {correct_roles / (correct_roles + incorrect_roles)}")