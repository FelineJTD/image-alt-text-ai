# %% [markdown]
# # Context Extractor AI
# This notebook contains AI model that is able to classify images into their roles (informative, decorative, functional, text, or complex). The model takes image and several text attributes as input and outputs a role.

# %% [markdown]
# ## Load Data


# %%
import json
import re
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
    print(str(e))

# %%
# installing some dependencies, CLIP was released in PyTorch

import numpy as np
import torch

# print("Torch version:", torch.__version__)

# %%
# clone the CLIP repository
# import subprocess

# subprocess.run(["git", "clone", "https://github.com/openai/CLIP.git"], check=True)

import sys
from pathlib import Path

try:
    clip_dir = Path(".").absolute() / "CLIP"
    sys.path.append(str(clip_dir))
    print(f"CLIP dir is: {clip_dir}")
except Exception as e:
    print(e)

import clip

# %%
import torch
from torchvision.transforms import Compose, Resize, CenterCrop, ToTensor, Normalize
from PIL import Image
import os
from packaging import version
import sklearn.preprocessing
import warnings

# %%
# Load pre-trained model
device = "cuda" if torch.cuda.is_available() else "cpu"
model, transform = clip.load("ViT-B/32", device=device)
model = model.eval()
print(f"Model dir: {os.path.expanduser('~/.cache/clip')}")

# %%
class CLIPCapDataset(torch.utils.data.Dataset):
    def __init__(self, data):
        self.data = data

    def __getitem__(self, idx):
        c_data = self.data[idx]
        c_data = clip.tokenize(f"On a website, this text: {c_data} is related to the image", truncate=True).squeeze()
        return {'caption': c_data}

    def __len__(self):
        return len(self.data)

# %%
def extract_all_captions(captions, model, device, batch_size=256, num_workers=8):
    data = torch.utils.data.DataLoader(
        CLIPCapDataset(captions),
        batch_size=batch_size, num_workers=num_workers, shuffle=False)
    all_text_features = []
    with torch.no_grad():
        for b in data:
            b = b['caption'].to(device)
            all_text_features.append(model.encode_text(b).cpu().numpy())
    all_text_features = np.vstack(all_text_features)
    return all_text_features

# %%
class CLIPImageDataset(torch.utils.data.Dataset):
    def __init__(self, data):
        self.data = data
        # only 224x224 ViT-B/32 supported for now
        self.preprocess = self._transform_test(224)

    def _transform_test(self, n_px):
        return Compose([
            Resize(n_px, interpolation=Image.BICUBIC),
            CenterCrop(n_px),
            lambda image: image.convert("RGB"),
            ToTensor(),
            Normalize((0.48145466, 0.4578275, 0.40821073), (0.26862954, 0.26130258, 0.27577711)),
        ])

    def __getitem__(self, idx):
        c_data = self.data[idx]
        image = Image.open(c_data)
        image = self.preprocess(image)
        return {'image':image}

    def __len__(self):
        return len(self.data)

# %%
def extract_all_images(images, model, device, batch_size=64, num_workers=8):
    data = torch.utils.data.DataLoader(
        CLIPImageDataset(images),
        batch_size=batch_size, num_workers=num_workers, shuffle=False)
    all_image_features = []
    with torch.no_grad():
        for b in data:
            b = b['image'].to(device)
            if device == 'cuda':
                b = b.to(torch.float16)
            all_image_features.append(model.encode_image(b).cpu().numpy())
    all_image_features = np.vstack(all_image_features)
    return all_image_features

# %%
def get_clip_score(model, images, candidates, device, w=2.5):
    '''
    get standard image-text clipscore.
    images can either be:
    - a list of strings specifying filepaths for images
    - a precomputed, ordered matrix of image features
    '''
    if isinstance(images, list):
        # need to extract image features
        images = extract_all_images(images, model, device)

    candidates = extract_all_captions(candidates, model, device)

    #as of numpy 1.21, normalize doesn't work properly for float16
    if version.parse(np.__version__) < version.parse('1.21'):
        images = sklearn.preprocessing.normalize(images, axis=1)
        candidates = sklearn.preprocessing.normalize(candidates, axis=1)
    else:
        warnings.warn(
            'due to a numerical instability, new numpy normalization is slightly different than paper results. '
            'to exactly replicate paper results, please use numpy version less than 1.21, e.g., 1.20.3.')
        images = images / np.sqrt(np.sum(images**2, axis=1, keepdims=True))
        candidates = candidates / np.sqrt(np.sum(candidates**2, axis=1, keepdims=True))

    per = w*np.clip(np.sum(images * candidates, axis=1), 0, None)
    return np.mean(per), per, candidates

# %%
# Test
# images=["./test_image/cat.jpg"]
# candidates = ["cat", "dog", "bird", "computer", "website", "evil", "cute cat", "orange cat"]
# model = model.eval()
# score, per, candidates = get_clip_score(model, images, candidates, device)
# print(f"Score: {score}")
# print(f"Per: {per}")
# print(f"Candidates: {candidates}")

# %% [markdown]
# # Prep Data

# %%
# Shuffle the data
import random
random.shuffle(data)

# %% [markdown]
# # Begin Eval

# %%
# CLIPScore evaluation

number_of_images = 100
# threshold = 0.65

init = {"is_relevant": 0, "num_data": 0}

max_similarity = 0
min_similarity = 1
prev_text_evals = [init.copy() for _ in range(5)]
next_text_evals = [init.copy() for _ in range(5)]
prev_text_evals_final = [0 for _ in range(5)]
next_text_evals_final = [0 for _ in range(5)]
all_similarities = []

progress = 0

for i_image in range(progress, min(number_of_images, len(data))):
    try:
        image = data[i_image]
        image_path = [f"{image_dir}{image['file_name']}"]
        class_captions = image["previous_texts"] + image["next_texts"]
        
        score, per, candidates = get_clip_score(model, image_path, class_captions, device)

        # Save the results
        for i, class_caption in enumerate(class_captions):
            if per[i] > max_similarity:
                max_similarity = per[i]
            if per[i] < min_similarity:
                min_similarity = per[i]
            if i < 5:
                prev_text_evals[i]["is_relevant"] += per[i]
            else:
                next_text_evals[i - 5]["is_relevant"] += per[i]
            if i < 5:
                prev_text_evals[i]["num_data"] += 1
            else:
                next_text_evals[i - 5]["num_data"] += 1
            all_similarities.append(per[i])

        # write the results to a file
        with open(f"{result_dir}/overview.txt", "w") as f:
            f.write(f"progress = {i_image}\n")
            f.write(f"max_similarity = {max_similarity}\n")
            f.write(f"min_similarity = {min_similarity}\n")
            f.write(f"prev_text_evals = {prev_text_evals}\n")
            f.write(f"next_text_evals = {next_text_evals}\n")

    except Exception as e:
        print(str(e))

# Calculate the percentage
for i in range(5):
    prev_text_evals_final[i] = (prev_text_evals[i]["is_relevant"] / prev_text_evals[i]["num_data"]) * 100
    next_text_evals_final[i] = (next_text_evals[i]["is_relevant"] / next_text_evals[i]["num_data"]) * 100

print("Previous text evaluations:")
print(prev_text_evals)
print("Next text evaluations:")
print(next_text_evals)

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

plt.figure(figsize=(10, 6))
plt.bar([f"prev-text-{i+1}" for i in range(5)], prev_text_evals_final, label="Percentage of relevant texts")
plt.bar([f"next-text-{i+1}" for i in range(5)], next_text_evals_final, label="Percentage of relevant texts")
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



