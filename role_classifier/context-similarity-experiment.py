import json
import re
from clipscore import get_clip_score

json_path = "../scraper/output-aut-en/output-en.json"
image_dir = "../scraper/output-aut-en/images/"
result_dir = "./clip_results"

try:
    # Read the JSON file
    with open(json_path, "r") as file:
        dirty_data = file.read()
        dirty_data = re.sub(r"\](\[\])*\[", ",", dirty_data)
        dirty_data = re.sub(r"\](\[\])*", "]", dirty_data)
        data = json.loads(dirty_data)

    # Print the first entry in the JSON data
    print(data[0])

    # Print the number of entries in the JSON data
    print(len(data))
    
except Exception as e:
    pass
    # print(str(e))

# Shuffle the data
import random
random.seed(42)
random.shuffle(data)

# %% [markdown]
# # Begin Eval

# %%
# CLIPScore evaluation

number_of_images = 100
threshold = 0.65

init = {"is_relevant": 0, "num_data": 0}

max_similarity = 0
min_similarity = 1
evals = [init.copy() for _ in range(12)]
evals_final = [0] * 12
all_similarities = []

progress = 0

for i_image in range(progress, min(number_of_images, len(data))):
    try:
        image = data[i_image]
        image_path = [f"{image_dir}{image['file_name']}"]

        # Ensure the list is 5 in length
        previous_texts = image["previous_texts"]
        previous_texts = previous_texts[:5]  # Slice to ensure a maximum of 5 elements
        previous_texts.extend([""] * (5 - len(previous_texts)))  # Extend with empty strings if less than 5

        # Assign back to image["previous_texts"]
        image["previous_texts"] = previous_texts

        # Ensure the list is 5 in length
        next_texts = image["next_texts"]
        next_texts = next_texts[:5]  # Slice to ensure a maximum of 5 elements
        next_texts.extend([""] * (5 - len(previous_texts)))  # Extend with empty strings if less than 5

        # Assign back to image["previous_texts"]
        image["next_texts"] = next_texts

        class_captions = image["previous_texts"] + image["next_texts"] + [image["doc_title"]] + [image["doc_description"]]

        score, per, candidates = get_clip_score(image_path, class_captions)

        # Save the results
        for i, class_caption in enumerate(class_captions):
            if (class_caption[i] != ""):
                if per[i] > max_similarity:
                    max_similarity = per[i]
                if per[i] < min_similarity:
                    min_similarity = per[i]

                if per[i] > threshold:
                    evals[i]["is_relevant"] += 1
                evals[i]["num_data"] += 1

                all_similarities.append(per[i])

        # write the results to a file
        with open(f"results_temp_threshold.txt", "w") as f:
            f.write(f"progress = {i_image}\n")
            f.write(f"max_similarity = {max_similarity}\n")
            f.write(f"min_similarity = {min_similarity}\n")
            f.write(f"evals = {evals}\n")

    except Exception as e:
        print(f"Image {i_image} failed:")

# Calculate the percentage
for i in range(12):
    evals_final[i] = (evals[i]["is_relevant"] / evals[i]["num_data"]) * 100


# print("Previous text evaluations:")
# print(prev_text_evals)
# print("Next text evaluations:")
# print(next_text_evals)

# %%
# from PIL import Image


# number_of_images = 10
# threshold = 25

# init = {"is_relevant": 0, "num_data": 0}

# max_similarity = 0
# min_similarity = 100
# prev_text_evals = [init.copy() for _ in range(5)]
# next_text_evals = [init.copy() for _ in range(5)]
# all_similarities = []
 

# for image in data[0:number_of_images]:
#     try:
#         class_captions = image["previous_texts"]
#         # Cut all the captions to the same length
#         class_captions = [f"On a website, this text: {caption} is related to the image" for caption in class_captions]
#         text_input = clip.tokenize(class_captions).to(device)

#         with torch.no_grad():
#             text_features = model.encode_text(text_input).float()
#             text_features /= text_features.norm(dim=-1, keepdim=True)
        
#         image_path = image["file_name"]
#         # Load the image
#         image_input = transform(Image.open(image_dir + image_path)).unsqueeze(0).to(device)
#         # Encode the image
#         with torch.no_grad():
#             image_features = model.encode_image(image_input).float()
#             image_features /= image_features.norm(dim=-1, keepdim=True)

#         # Display the results
#         text_probs = (100.0 * image_features @ text_features.T)
#         text_probs = text_probs.cpu()
#         print("Prev: ", text_probs)

#         # Save the results
#         for i, class_caption in enumerate(class_captions):
#             if text_probs[0][i].item() > max_similarity:
#                 max_similarity = text_probs[0][i].item()
#             if text_probs[0][i].item() < min_similarity:
#                 min_similarity = text_probs[0][i].item()
#             if text_probs[0][i].item() > threshold:
#                 prev_text_evals[i]["is_relevant"] += 1
#             all_similarities.append(text_probs[0][i].item())
#             prev_text_evals[i]["num_data"] += 1

#         # Next text
#         class_captions = image["next_texts"]
#         # Cut all the captions to the same length
#         class_captions = [f"On a website, this text: {caption} is related to the image" for caption in class_captions]
#         text_input = clip.tokenize(class_captions).to(device)

#         with torch.no_grad():
#             text_features = model.encode_text(text_input).float()
#             text_features /= text_features.norm(dim=-1, keepdim=True)

#         # Display the results
#         text_probs = (100.0 * image_features @ text_features.T)
#         text_probs = text_probs.cpu()
#         print("Next: ", text_probs)

#         # Save the results
#         for i, class_caption in enumerate(class_captions):
#             if text_probs[0][i].item() > max_similarity:
#                 max_similarity = text_probs[0][i].item()
#             if text_probs[0][i].item() < min_similarity:
#                 min_similarity = text_probs[0][i].item()
#             if text_probs[0][i].item() > threshold:
#                 next_text_evals[i]["is_relevant"] += 1
#             all_similarities.append(text_probs[0][i].item())
#             next_text_evals[i]["num_data"] += 1

#     except Exception as e:
#         print(str(e))

# # Calculate the percentage
# for i in range(5):
#     prev_text_evals[i]["is_relevant"] = (prev_text_evals[i]["is_relevant"] / prev_text_evals[i]["num_data"]) * 100
#     next_text_evals[i]["is_relevant"] = (next_text_evals[i]["is_relevant"] / next_text_evals[i]["num_data"]) * 100

# print("Previous text evaluations:")
# print(prev_text_evals)
# print("Next text evaluations:")
# print(next_text_evals)

# %%
# Plot the results
import matplotlib.pyplot as plt

plt.figure(figsize=(12, 6))
plt.bar([f"prev-text-{i+1}" for i in range(12)], evals_final, label="Percentage of relevant texts")
# plt.bar([f"next-text-{i+1}" for i in range(5)], next_text_evals_final, label="Percentage of relevant texts")
plt.legend(loc="upper right")

# Tilt the x-axis labels
plt.xticks(rotation=45)

plt.show()


# %%
print(max_similarity)
print(min_similarity)

# %%
# Plot all_similarities
import matplotlib.pyplot as plt

plt.hist(all_similarities, bins=50)
plt.title("Similarity distribution")
plt.show()



