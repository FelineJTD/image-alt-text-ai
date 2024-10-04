import json
import re
import random

input_path = "../scraper/output-aut-en/output-en.json"
output_path = "./output-en-random.json"

try:
    # Read the JSON file
    with open(input_path, "r") as file:
        dirty_data = file.read()
        dirty_data = re.sub(r"\](\[\])*\[", ",", dirty_data)
        dirty_data = re.sub(r"\](\[\])*", "]", dirty_data)
        data = json.loads(dirty_data)
        print("Data loaded: " + str(len(data)) + " images")

    # Randomize the data
    random.shuffle(data)
    random.shuffle(data)
    random.shuffle(data)

    # Write the JSON file
    with open(output_path, "w") as file:
        json.dump(data, file, indent=4)
    
except Exception as e:
    print(str(e))