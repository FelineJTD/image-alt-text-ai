number_of_images = 10
threshold = 0.65

init = {"is_relevant": 0, "num_data": 0}

max_similarity = 0
min_similarity = 1
prev_text_evals = [init.copy() for _ in range(5)]
next_text_evals = [init.copy() for _ in range(5)]
prev_text_evals_final = [0 for _ in range(5)]
next_text_evals_final = [0 for _ in range(5)]
all_similarities = []

def download_image(image_src, image_name):
    import requests
    import os

    # Get the image
    response = requests.get(image_src)

    # Save the image
    with open(image_name, "wb") as f:
        f.write(response.content)

    return image_name

for image in data[0:number_of_images]:
    try:
        image_src = image["src"]
        # Download image from web and store it in local
        image_src = download_image(image_src)


        
        class_captions = image["previous_texts"] + image["next_texts"]
        
        score, per, candidates = get_clip_score(model, image_src, class_captions, device)

        # Save the results
        for i, class_caption in enumerate(class_captions):
            if per[i] > max_similarity:
                max_similarity = per[i]
            if per[i] < min_similarity:
                min_similarity = per[i]
            if per[i] > threshold:
                if i < 5:
                    prev_text_evals[i]["is_relevant"] += 1
                else:
                    next_text_evals[i - 5]["is_relevant"] += 1
            all_similarities.append(per[i])
            if i < 5:
                prev_text_evals[i]["num_data"] += 1
            else:
                next_text_evals[i - 5]["num_data"] += 1

        # write the results to a file
        with open("clip_results.txt", "w") as f:
            f.write(f"{prev_text_evals}\n")
            f.write(f"{next_text_evals}\n")

    except Exception as e:
        print(str(e))

# Calculate the percentage
# for i in range(5):
#     prev_text_evals_final[i] = (prev_text_evals[i]["is_relevant"] / prev_text_evals[i]["num_data"]) * 100
#     next_text_evals_final[i] = (next_text_evals[i]["is_relevant"] / next_text_evals[i]["num_data"]) * 100

print("Previous text evaluations:")
print(prev_text_evals)
print("Next text evaluations:")
print(next_text_evals)