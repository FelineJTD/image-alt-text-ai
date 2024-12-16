# Read finetune-final.jsonl, shuffle the data, then split for test and train datasets. Save the test dataset as test.jsonl and the train dataset as train.jsonl. The test dataset should contain 20% of the data.
import random

with open('finetune-whitelisted.jsonl', 'r') as file:
    data = file.readlines()

print("Total data:", len(data))

random.seed(42)
random.shuffle(data)
import json

# Split the data into test and train datasets, with 20% of the data in the test dataset
test_data = data[:int(0.2 * len(data))]
train_data = data[int(0.2 * len(data)):]

# Count each role in the test and train datasets
test_data_roles = {}
train_data_roles = {}

for line in test_data:
    role = json.loads(line)["messages"][2]["content"]
    if role in test_data_roles:
        test_data_roles[role] += 1
    else:
        test_data_roles[role] = 1

for line in train_data:
    role = json.loads(line)["messages"][2]["content"]
    if role in train_data_roles:
        train_data_roles[role] += 1
    else:
        train_data_roles[role] = 1

print("Test data roles:", test_data_roles)
print("Total test data:", len(test_data))
print("Train data roles:", train_data_roles)
print("Total train data:", len(train_data))

with open('test-whitelisted.jsonl', 'w') as file:
    file.writelines(test_data)

with open('train-whitelisted.jsonl', 'w') as file:
    file.writelines(train_data)