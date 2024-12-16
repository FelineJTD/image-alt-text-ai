import matplotlib.pyplot as plt

# CONFIG
json_path = "../scraper/output-aut-en/output-en.json"
image_dir = "../scraper/output-aut-en/images/"
result_dir = "./clip_results_full"
number_of_images = 500
threshold = 0.5905375164518996
random_seed = 42
elements = ["prev-text-1", "prev-text-2", "prev-text-3", "prev-text-4", "prev-text-5", "next-text-1", "next-text-2", "next-text-3", "next-text-4", "next-text-5", "doc-title", "doc-description", "prev-sib-title", "next-sib-title", "prev-sib-text-1", "prev-sib-text-2", "prev-sib-text-3", "prev-sib-text-4", "prev-sib-text-5", "next-sib-text-1", "next-sib-text-2", "next-sib-text-3", "next-sib-text-4", "next-sib-text-5"]


# EVALUATION
# CLIPScore evaluation
init = {"relevance_avg": 0, "is_relevant": 0, "num_data": 0}

progress = 0
max_similarity = {"prev-text": 0, "next-text": 0, "doc-title": 0, "doc-description": 0}
min_similarity = {"prev-text": 1, "next-text": 1, "doc-title": 1, "doc-description": 1}
evals = {}
evals_percentage = {}
evals_threshold = {}
all_similarities = {}

# Read the progress from the file
try:
    with open(f"{result_dir}/results.txt", "r") as f:
        lines = f.readlines()
        for line in lines:
            if "progress" in line:
                progress = int(line.split("=")[1].strip())
            if "max_similarity" in line:
                max_similarity = eval(line.split("=")[1].strip())
            if "min_similarity" in line:
                min_similarity = eval(line.split("=")[1].strip())
            if "evals" in line:
                evals = eval(line.split("=")[1].strip())
            if "all_similarities" in line:
                all_similarities = eval(line.split("=")[1].strip())
        print("Loaded progress: ", progress)
        print("Loaded max_similarity: ", max_similarity)
        print("Loaded min_similarity: ", min_similarity)
        print("Loaded evals: ", evals)
except Exception as e:
    print(str(e))

# Calculate relevant images count
for key in all_similarities:
    relevant = 0
    for similarity in all_similarities[key]:
        if similarity >= threshold:
            relevant += 1

    evals_threshold[key] = (relevant / len(all_similarities[key])) * 100

# Calculate the average
for element in elements:
    evals_percentage[element] = (evals[element]["relevance_avg"] / evals[element]["num_data"])
    # evals_threshold[element] = (evals[element]["is_relevant"] / evals[element]["num_data"]) * 100

print("Loaded evals_percentage: ", evals_percentage)
print("Loaded evals_threshold: ", evals_threshold)

plt.style.use('seaborn-v0_8-muted')


all_similarities_flat = []
for key in all_similarities:
    all_similarities_flat.extend(all_similarities[key])

average_similarity = sum(all_similarities_flat) / len(all_similarities_flat)

print("Average similarity: ", average_similarity)

# PLOT THE RESULTS
# Plot all_similarities
plt.hist(all_similarities_flat, bins=50)

plt.title("Distribusi Peroehan CLIPScore")
# Save the plot
plt.savefig(f"{result_dir}/similarities.png")

doc_title_flat = []
doc_description_flat = []
prev_text_flat = []
next_text_flat = []
prev_sib_flat = []
next_sib_flat = []
prev_sib_title_flat = []
next_sib_title_flat = []

for key in evals_percentage:
    print(key)
    if "doc-title" in key:
        doc_title_flat.append(evals_percentage[key])
    elif "doc-description" in key:
        doc_description_flat.append(evals_percentage[key])
    elif "prev-text" in key:
        prev_text_flat.append(evals_percentage[key])
    elif "next-text" in key:
        next_text_flat.append(evals_percentage[key])
    elif "prev-sib-title" in key:
        prev_sib_title_flat.append(evals_percentage[key])
    elif "next-sib-title" in key:
        next_sib_title_flat.append(evals_percentage[key])
    elif "prev-sib" in key:
        prev_sib_flat.append(evals_percentage[key])
    elif "next-sib" in key:
        next_sib_flat.append(evals_percentage[key])


# Plot the evaluation results
plt.figure(figsize=(12, 6))
plt.bar(["doc-title"], doc_title_flat)
plt.bar(["doc-description"], doc_description_flat)
plt.bar([f"prev-text-{i+1}" for i in range(5)], prev_text_flat)
plt.bar([f"next-text-{i+1}" for i in range(5)], next_text_flat)
plt.bar([f"prev-sibling-{i+1}" for i in range(5)], prev_sib_flat)
plt.bar([f"next-sibling-{i+1}" for i in range(5)], next_sib_flat)
plt.bar(["prev-sib-title"], prev_sib_title_flat)
plt.bar(["next-sib-title"], next_sib_title_flat)
plt.title("Rata-rata Perolehan CLIPScore Tiap Kelompok Elemen")

# for i, value in enumerate(evals_percentage):
#     plt.text(i, value, f"{value:.3f}", ha='center', va='bottom')

# Tilt the x-axis labels
plt.xticks(rotation=24)
# Save the plot
plt.savefig(f"{result_dir}/evaluation-avg.png")

threshold_doc_title_flat = []
threshold_doc_description_flat = []
threshold_prev_text_flat = []
threshold_next_text_flat = []
threshold_prev_sib_flat = []
threshold_next_sib_flat = []
threshold_prev_sib_title_flat = []
threshold_next_sib_title_flat = []

for key in evals_threshold:
    print(key)
    if "doc-title" in key:
        threshold_doc_title_flat.append(evals_threshold[key])
    elif "doc-description" in key:
        threshold_doc_description_flat.append(evals_threshold[key])
    elif "prev-text" in key:
        threshold_prev_text_flat.append(evals_threshold[key])
    elif "next-text" in key:
        threshold_next_text_flat.append(evals_threshold[key])
    elif "prev-sib-title" in key:
        threshold_prev_sib_title_flat.append(evals_threshold[key])
    elif "next-sib-title" in key:
        threshold_next_sib_title_flat.append(evals_threshold[key])
    elif "prev-sib" in key:
        threshold_prev_sib_flat.append(evals_threshold[key])
    elif "next-sib" in key:
        threshold_next_sib_flat.append(evals_threshold[key])

all_thresholds = threshold_doc_title_flat + threshold_doc_description_flat + threshold_prev_text_flat + threshold_next_text_flat + threshold_prev_sib_flat + threshold_next_sib_flat + threshold_prev_sib_title_flat + threshold_next_sib_title_flat

# Plot the evaluation results
plt.figure(figsize=(12, 6))
plt.bar(["doc-title"], threshold_doc_title_flat)
plt.bar(["doc-description"], threshold_doc_description_flat)
plt.bar([f"prev-text-{i+1}" for i in range(5)], threshold_prev_text_flat)
plt.bar([f"next-text-{i+1}" for i in range(5)], threshold_next_text_flat)
plt.bar([f"prev-sibling-{i+1}" for i in range(5)], threshold_prev_sib_flat)
plt.bar([f"next-sibling-{i+1}" for i in range(5)], threshold_next_sib_flat)
plt.bar(["prev-sib-title"], threshold_prev_sib_title_flat)
plt.bar(["next-sib-title"], threshold_next_sib_title_flat)

plt.title("Persentase Teks yang Relevan Tiap Kelompok Elemen")

for i, value in enumerate(all_thresholds):
    plt.text(i, value, f"{value:.3f}%", ha='center', va='bottom')

# Tilt the x-axis labels
plt.xticks(rotation=24)
# Save the plot
plt.savefig(f"{result_dir}/evaluation-percent.png")

# Print the max and min similarity
# print("Max similarity: ", max_similarity)
# print("Min similarity: ", min_similarity)
# print("Average similarity: ", sum(all_similarities) / len(all_similarities))
