import random

with open('human-data-not-filtered.jsonl', 'r') as file:
    data = file.readlines()

print("Total data:", len(data))

random.seed(42)
random.shuffle(data)
import json

# Get 5 data for each role
roles = {
    "informative": 0,
    "functional": 0,
    "decorative": 0,
    "complex": 0
}
# data = [line for line in data if (json.loads(line)["messages"][2]["content"] in roles and roles[json.loads(line)["messages"][2]["content"]] < 5)]
data_filtered = []
for i in range(len(data)):
    role = json.loads(data[i])["role"]
    if roles[role] < 3:
        data_filtered.append(data[i])
        roles[role] += 1

print("Total data:", len(data_filtered))

with open('human-data.jsonl', 'w') as file:
    file.writelines(data_filtered)