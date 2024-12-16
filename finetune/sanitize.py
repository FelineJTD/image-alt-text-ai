# Read finetune-final.jsonl, shuffle the data, then split for test and train datasets. Save the test dataset as test.jsonl and the train dataset as train.jsonl. The test dataset should contain 20% of the data.
import json

with open('train.jsonl', 'r') as file:
    data = file.readlines()

print("Total data:", len(data))

domains = []

# Count each role in the test and train datasets
test_data_roles = {}
train_data_roles = {}

for line in data:
    src = json.loads(line)["messages"][1]["content"][0]["image_url"]["url"]

    if src in domains:
        continue
    else:
        domains.append(src)

with open('domains.json', 'w') as file:
    json.dump(domains, file)