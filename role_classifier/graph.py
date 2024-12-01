import matplotlib.pyplot as plt

# CONFIG
json_path = "../scraper/output-aut-en/output-en.json"
image_dir = "../scraper/output-aut-en/images/"
result_dir = "./clip_results_fixed"
number_of_images = 500
threshold = 0.65
random_seed = 42


# EVALUATION
# CLIPScore evaluation
init = {"relevance_avg": 0, "is_relevant": 0, "num_data": 0}

progress = 0
max_similarity = {"prev-text": 0, "next-text": 0, "doc-title": 0, "doc-description": 0}
min_similarity = {"prev-text": 1, "next-text": 1, "doc-title": 1, "doc-description": 1}
evals = [init.copy() for _ in range(12)]
evals_percentage = [0] * 12
evals_threshold = [0] * 12
all_similarities = []

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

# Calculate the average
for i in range(12):
    evals_percentage[i] = (evals[i]["relevance_avg"] / evals[i]["num_data"])
    evals_threshold[i] = (evals[i]["is_relevant"] / evals[i]["num_data"]) * 100

print("Loaded evals_percentage: ", evals_percentage)
print("Loaded evals_threshold: ", evals_threshold)

plt.style.use('seaborn-v0_8-muted')


# PLOT THE RESULTS
# Plot all_similarities
plt.hist(all_similarities, bins=50)
plt.title("Distribusi Peroehan CLIPScore")
# Save the plot
plt.savefig(f"{result_dir}/similarities.png")

# Plot the evaluation results
plt.figure(figsize=(12, 6))
plt.bar([f"prev-text-{i+1}" for i in range(5)], evals_percentage[0:5])
plt.bar([f"next-text-{i+1}" for i in range(5)], evals_percentage[5:10])
plt.bar(["doc-title"], evals_percentage[10:11])
plt.bar(["doc-description"], evals_percentage[11:12])
plt.title("Rata-rata Perolehan CLIPScore Tiap Kelompok Elemen")

for i, value in enumerate(evals_percentage):
    plt.text(i, value, f"{value:.3f}", ha='center', va='bottom')

# Tilt the x-axis labels
plt.xticks(rotation=24)
# Save the plot
plt.savefig(f"{result_dir}/evaluation-avg.png")

# Plot the evaluation results
plt.figure(figsize=(12, 6))
plt.bar([f"prev-text-{i+1}" for i in range(5)], evals_threshold[0:5])
plt.bar([f"next-text-{i+1}" for i in range(5)], evals_threshold[5:10])
plt.bar(["doc-title"], evals_threshold[10:11])
plt.bar(["doc-description"], evals_threshold[11:12])
plt.title("Persentase Teks yang Relevan Tiap Kelompok Elemen")

for i, value in enumerate(evals_threshold):
    plt.text(i, value, f"{value:.3f}%", ha='center', va='bottom')

# Tilt the x-axis labels
plt.xticks(rotation=24)
# Save the plot
plt.savefig(f"{result_dir}/evaluation-percent.png")

# Print the max and min similarity
print("Max similarity: ", max_similarity)
print("Min similarity: ", min_similarity)
