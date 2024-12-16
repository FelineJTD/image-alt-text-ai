import random
import json
import re
import matplotlib.pyplot as plt
from clipscore import get_clip_score
import time
import os


# CONFIG
json_path = "../scraper/output-aut-en-full/output.json"
image_dir = "../scraper/output-aut-en-full/images/"
result_dir = "./clip_results_full"
number_of_images = 2000
threshold = 0.65
# random_seed = 42


# START THE TIMER
start_time = time.time()


# READ AND PREPARE THE DATA
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
    print("Images found: ", len(data))
    
except Exception as e:
    print(str(e))

# Shuffle the data
# random.seed(random_seed)
# random.shuffle(data)


# EVALUATION
# CLIPScore evaluation
init = {"relevance_avg": 0, "is_relevant": 0, "num_data": 0}

progress = 0
# max_similarity = {"prev-text": 0, "next-text": 0, "doc-title": 0, "doc-description": 0}
# min_similarity = {"prev-text": 1, "next-text": 1, "doc-title": 1, "doc-description": 1}
evals = {
    "prev-text-1": init.copy(),
    "prev-text-2": init.copy(),
    "prev-text-3": init.copy(),
    "prev-text-4": init.copy(),
    "prev-text-5": init.copy(),
    "next-text-1": init.copy(),
    "next-text-2": init.copy(),
    "next-text-3": init.copy(),
    "next-text-4": init.copy(),
    "next-text-5": init.copy(),
    "prev-sib-text-1": init.copy(),
    "prev-sib-text-2": init.copy(),
    "prev-sib-text-3": init.copy(),
    "prev-sib-text-4": init.copy(),
    "prev-sib-text-5": init.copy(),
    "next-sib-text-1": init.copy(),
    "next-sib-text-2": init.copy(),
    "next-sib-text-3": init.copy(),
    "next-sib-text-4": init.copy(),
    "next-sib-text-5": init.copy(),
    "prev-sib-title": init.copy(),
    "next-sib-title": init.copy(),
    "doc-title": init.copy(),
    "doc-description": init.copy()
}
evals_final = [0] * 12
all_similarities = {
    "prev-text-1": [],
    "prev-text-2": [],
    "prev-text-3": [],
    "prev-text-4": [],
    "prev-text-5": [],
    "next-text-1": [],
    "next-text-2": [],
    "next-text-3": [],
    "next-text-4": [],
    "next-text-5": [],
    "prev-sib-text-1": [],
    "prev-sib-text-2": [],
    "prev-sib-text-3": [],
    "prev-sib-text-4": [],
    "prev-sib-text-5": [],
    "next-sib-text-1": [],
    "next-sib-text-2": [],
    "next-sib-text-3": [],
    "next-sib-text-4": [],
    "next-sib-text-5": [],
    "prev-sib-title": [],
    "next-sib-title": [],
    "doc-title": [],
    "doc-description": []
}

# Create result_dir if it does not exist
try:
    os.makedirs(result_dir)
except Exception as e:
    print(str(e))

# Read the progress from the file
try:
    with open(f"{result_dir}/results.txt", "r") as f:
        lines = f.readlines()
        for line in lines:
            if "progress" in line:
                progress = int(line.split("=")[1].strip())
            # if "max_similarity" in line:
            #     max_similarity = eval(line.split("=")[1].strip())
            # if "min_similarity" in line:
            #     min_similarity = eval(line.split("=")[1].strip())
            if "evals" in line:
                evals = eval(line.split("=")[1].strip())
            if "all_similarities" in line:
                all_similarities = eval(line.split("=")[1].strip())
        print("Loaded progress: ", progress)
        # print("Loaded max_similarity: ", max_similarity)
        # print("Loaded min_similarity: ", min_similarity)
        print("Loaded evals: ", evals)
except Exception as e:
    print(str(e))

# Loop through the data
for i_image in range(progress + 1, min(number_of_images, len(data))):
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

        # Ensure the list is 5 in length
        prev_sib_texts = image["prev_siblings"]
        prev_sib_texts = prev_sib_texts[:5]  # Slice to ensure a maximum of 5 elements
        prev_sib_texts.extend([""] * (5 - len(prev_sib_texts)))  # Extend with empty strings if less than 5

        # Assign back to image["prev_siblings"]
        image["prev_siblings"] = prev_sib_texts

        # Ensure the list is 5 in length
        next_sib_texts = image["next_siblings"]
        next_sib_texts = next_sib_texts[:5]  # Slice to ensure a maximum of 5 elements
        next_sib_texts.extend([""] * (5 - len(next_sib_texts)))  # Extend with empty strings if less than 5

        # Assign back to image["next_siblings"]
        image["next_siblings"] = next_sib_texts

        # Ensure the list is 1 in length
        prev_title = [image["img_prev_header"]]
        next_title = [image["img_next_header"]]
        image["img_prev_header"] = prev_title
        image["img_next_header"] = next_title

        # Ensure the list is 1 in length
        doc_title = [image["doc_title"]]
        doc_description = [image["doc_description"]]
        image["doc_title"] = doc_title
        image["doc_description"] = doc_description

        class_captions = image["previous_texts"] + image["next_texts"] + image["doc_title"] + image["doc_description"] + image["prev_siblings"] + image["next_siblings"] + image["img_prev_header"] + image["img_next_header"]

        # Ensure class_captions is 24 in length
        class_captions = class_captions[:24]
        class_captions.extend([""] * (24 - len(class_captions)))

        score, per, candidates = get_clip_score(image_path, class_captions)

        # Save the results
        for i, class_caption in enumerate(class_captions):
            if (class_caption != ""):
                element = ""
                if i < 5:
                    element = f"prev-text-{i+1}"
                    # if per[i] > max_similarity["prev-text"]:
                    #     max_similarity["prev-text"] = per[i]
                    # if per[i] < min_similarity["prev-text"]:
                    #     min_similarity["prev-text"] = per[i]
                elif i < 10:
                    element = f"next-text-{i-4}"
                    # if per[i] > max_similarity["next-text"]:
                    #     max_similarity["next-text"] = per[i]
                    # if per[i] < min_similarity["next-text"]:
                    #     min_similarity["next-text"] = per[i]
                elif i == 10:
                    element = "doc-title"
                    # if per[i] > max_similarity["doc-title"]:
                    #     max_similarity["doc-title"] = per[i]
                    # if per[i] < min_similarity["doc-title"]:
                    #     min_similarity["doc-title"] = per[i]
                elif i == 11:
                    element = "doc-description"
                    # if per[i] > max_similarity["doc-description"]:
                    #     max_similarity["doc-description"] = per[i]
                    # if per[i] < min_similarity["doc-description"]:
                    #     min_similarity["doc-description"] = per[i]
                elif i < 17:
                    element = f"prev-sib-text-{i-11}"
                    # if per[i] > max_similarity["prev-sib-text"]:
                    #     max_similarity["prev-sib-text"] = per[i]
                    # if per[i] < min_similarity["prev-sib-text"]:
                    #     min_similarity["prev-sib-text"] = per[i]
                elif i < 22:
                    element = f"next-sib-text-{i-16}"
                    # if per[i] > max_similarity["next-sib-text"]:
                    #     max_similarity["next-sib-text"] = per[i]
                    # if per[i] < min_similarity["next-sib-text"]:
                    #     min_similarity["next-sib-text"] = per[i]
                elif i == 22:
                    element = "prev-sib-title"
                    # if per[i] > max_similarity["prev-sib-title"]:
                    #     max_similarity["prev-sib-title"] = per[i]
                    # if per[i] < min_similarity["prev-sib-title"]:
                    #     min_similarity["prev-sib-title"] = per[i]
                elif i == 23:
                    element = "next-sib-title"
                    # if per[i] > max_similarity["next-sib-title"]:
                    #     max_similarity["next-sib-title"] = per[i]
                    # if per[i] < min_similarity["next-sib-title"]:
                    #     min_similarity["next-sib-title"] = per[i]

                if per[i] > threshold:
                    evals[element]["is_relevant"] += 1
                evals[element]["relevance_avg"] += per[i]
                evals[element]["num_data"] += 1

                all_similarities[element].append(per[i])

        # write the results to a file
        with open(f"{result_dir}/results.txt", "w") as f:
            f.write(f"progress = {i_image}\n")
            # f.write(f"max_similarity = {max_similarity}\n")
            # f.write(f"min_similarity = {min_similarity}\n")
            f.write(f"evals = {evals}\n")
            f.write(f"all_similarities = {all_similarities}\n")

    except Exception as e:
        print(f"Image {i_image} failed: {str(e)}")
        # write to error log
        with open(f"{result_dir}/errors.txt", "a") as f:
            f.write(f"Image {i_image} failed: {str(e)}\n")


# Calculate the average
# for i in range(12):
#     evals_final[i] = (evals[i]["relevance_avg"] / evals[i]["num_data"]) * 100


# END THE TIMER
end_time = time.time()
time_taken = end_time - start_time


# PRINT THE TIME TAKEN
print("Time taken: ", time_taken)
print("Average time per image: ", time_taken / number_of_images)


# PLOT THE RESULTS
# Plot all_similarities
# plt.hist(all_similarities, bins=50)
# plt.title("Similarity distribution")
# # Save the plot
# plt.savefig(f"{result_dir}/similarities.png")
# # Show the plot
# plt.show()

# # Plot the evaluation results
# plt.figure(figsize=(12, 6))
# plt.bar([f"prev-text-{i+1}" for i in range(5)], evals_final[0:5], label="Percentage of relevant texts")
# plt.bar([f"next-text-{i+1}" for i in range(5)], evals_final[5:10], label="Percentage of relevant texts")
# plt.bar(["doc-title"], evals_final[10:11], label="Percentage of relevant texts")
# plt.bar(["doc-description"], evals_final[11:12], label="Percentage of relevant texts")
# plt.legend(loc="upper right")

# Tilt the x-axis labels
# plt.xticks(rotation=45)
# # Save the plot
# plt.savefig(f"{result_dir}/evaluation.png")
# # Show the plot
# plt.show()

# # Print the max and min similarity
# print("Max similarity: ", max_similarity)
# print("Min similarity: ", min_similarity)
