import os
import json
import pandas as pd

def load_data(json_dir):
    # Initialize empty lists to store the image links and textual contexts
    srcs = []
    file_names = []
    roles = []
    alts = []
    attrs = []
    a_button_parents = []
    previous_texts = []
    next_texts = []
    textual_contexts = []

    images = []

    # Loop through each JSON file in the directory
    for filename in os.listdir(json_dir):
        if filename.endswith(".json"):
            # Read the JSON file
            with open(os.path.join(json_dir, filename), "r") as file:
                data = json.load(file)
            
            # Extract the image link and textual context from the JSON data
            whole_text = data["text"]
            sub_images = data["images"]

            images.extend(sub_images)

            for image in images:
                # {
                #     "src": "http://donutworrybehappy.eu/getattachment/71afc349-9d82-4861-9324-1d304061f188/hero-section.aspx",
                #     "file_name": "./images/donutworrybehappy.eu/image_12.jpg",
                #     "role": "text",
                #     "alt": "Strawjelly Jam: fresh strawberry-style glaze with Belgian chocolate cover",
                #     "attrs": {
                #         "src": "/getattachment/71afc349-9d82-4861-9324-1d304061f188/hero-section.aspx?",
                #         "class": [
                #             "StyledMobileImage-sc-y8dlz5",
                #             "cZQlpK"
                #         ]
                #     },
                #     "a_button_parent": "None",
                #     "previous_text": "",
                #     "next_text": "Donut Worry Be Happy"
                # }
                src = image["src"]
                file_name = image["file_name"]
                role = image["role"]
                alt = image["alt"]
                attr = image["attrs"]
                a_button_parent = image["a_button_parent"]
                previous_text = image["previous_text"]
                next_text = image["next_text"]
                textual_context = whole_text
                
                # Append the image link and textual context to the respective lists
                srcs.append(src)
                file_names.append(file_name)
                roles.append(role)
                alts.append(alt)
                attrs.append(attrs)
                a_button_parents.append(a_button_parent)
                previous_texts.append(previous_text)
                next_texts.append(next_text)
                textual_contexts.append(textual_context)

    # Create a dataframe from the lists
    df = pd.DataFrame(images)

    # Display the number data points in the dataframe
    print(f"Number of data points: {df.shape[0]}")

    return df
    