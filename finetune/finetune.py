import json
import os
import random

system_prompt = '''
You are part of a team tasked with generating role-aware and context-aware image alt texts for images on websites. Your role is to identify the role of the given image in the website according to the definitions provided by the WCAG Web Accessibility Initiative (WAI) outlined below.


1. informative: Images that graphically represent concepts and information, typically pictures, photos, and illustrations. The text alternative should be at least a short description conveying the essential information presented by the image.

2. decorative: The only purpose of an image is to add visual decoration to the page, rather than to convey information that is important to understanding the page. This includes images that are considered eye candy or used for visual effect. Classify the image to decorative if having a null alt-text (alt="") will not result in any loss of information.

3. functional: Images used as a link or as a button, which carry a functionality to the page. Examples of such images are a printer icon to represent the print function or a button to submit a form. The alt text should describe the functionality of the link or button rather than the visual image.

4. complex: Images used to convey data or detailed information, such as graphs or charts. Alt texts provide a complete text equivalent of the data or information provided in the image as the text alternative.


As each role needs to be handled differently when generating alt texts, your output will be used to help another team member write the most suitable alt text that is role-aware and contex-aware for the image to help create more accessible websites.

Return only the role of the image from the list above. Return the role as a single word without any enclosing bracket, e.g., informative, decorative, functional, text, or complex. THIS IS IMPORTANT! RETURN ONLY THE ROLE OF THE IMAGE.

'''

# Main
if __name__ == "__main__":
    json_dir = "../scraper/output"

    filenames = os.listdir(json_dir)

    # Shuffle the filenames
    random.seed(42)
    random.shuffle(filenames)

    # Loop through each JSON file in the directory
    for filename in os.listdir(json_dir)[1:10]:
        if filename.endswith(".json"):
            try:
                # Read the JSON file
                with open(os.path.join(json_dir, filename), "r") as file:
                    data = json.load(file)
                
                # Extract the image link and textual context from the JSON data
                whole_text = data["text"]
                sub_images = data["images"]

                results = []

                for image in sub_images:
                    finetune_data = {
                        "messages": [{
                            "role": "system", 
                            "content": "Marv is a factual chatbot that is also sarcastic."
                        }, {
                            "role": "user", 
                            "content": "What's the capital of France?"
                        }, {
                            "role": "assistant", 
                            "content": "Paris, as if everyone doesn't know that already."
                        }]}

                # Save the final state to a JSON file
                with open(f"./finetune.jsonl", "a") as file:
                    json.dump(finetune_data, file)
                    file.write("\n")

            except Exception as e:
                print(str(e))