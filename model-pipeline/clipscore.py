# # %%
# # installing some dependencies, CLIP was released in PyTorch

# import numpy as np
# import torch
# import requests
# from io import BytesIO

# # print("Torch version:", torch.__version__)

# # %%
# # clone the CLIP repository
# # import subprocess

# # subprocess.run(["git", "clone", "https://github.com/openai/CLIP.git"], check=True)

# import sys
# from pathlib import Path

# try:
#     clip_dir = Path(".").absolute() / "CLIP"
#     sys.path.append(str(clip_dir))
#     print(f"CLIP dir is: {clip_dir}")
# except Exception as e:
#     print(e)

# import clip

# # %%
# import torch
# from torchvision.transforms import Compose, Resize, CenterCrop, ToTensor, Normalize
# from PIL import Image
# import os
# from packaging import version
# import sklearn.preprocessing
# import warnings

# # %%
# # Load pre-trained model
# device = "cuda" if torch.cuda.is_available() else "cpu"
# model, transform = clip.load("ViT-B/32", device=device)
# model = model.eval()
# print(f"Model dir: {os.path.expanduser('~/.cache/clip')}")

# # %%
# class CLIPCapDataset(torch.utils.data.Dataset):
#     def __init__(self, data):
#         self.data = data

#     def __getitem__(self, idx):
#         c_data = self.data[idx]
#         c_data = clip.tokenize(f"This text: {c_data} is related to the image", truncate=True).squeeze()
#         return {'caption': c_data}

#     def __len__(self):
#         return len(self.data)

# # %%
# def extract_all_captions(captions, model, device, batch_size=256, num_workers=8):
#     data = torch.utils.data.DataLoader(
#         CLIPCapDataset(captions),
#         batch_size=batch_size, num_workers=num_workers, shuffle=False)
#     all_text_features = []
#     with torch.no_grad():
#         for b in data:
#             b = b['caption'].to(device)
#             all_text_features.append(model.encode_text(b).cpu().numpy())
#     all_text_features = np.vstack(all_text_features)
#     return all_text_features

# # %%
# class CLIPImageDataset(torch.utils.data.Dataset):
#     def __init__(self, data):
#         self.data = data
#         # only 224x224 ViT-B/32 supported for now
#         self.preprocess = self._transform_test(224)

#     def _transform_test(self, n_px):
#         return Compose([
#             Resize(n_px, interpolation=Image.BICUBIC),
#             CenterCrop(n_px),
#             lambda image: image.convert("RGB"),
#             ToTensor(),
#             Normalize((0.48145466, 0.4578275, 0.40821073), (0.26862954, 0.26130258, 0.27577711)),
#         ])

#     def __getitem__(self, idx):
#         url = self.data[idx]
#         response = requests.get(url)
#         image = Image.open(BytesIO(response.content))
#         image = self.preprocess(image)
#         return {'image':image}

#     def __len__(self):
#         return len(self.data)

# # %%
# def extract_all_images(images, model, device, batch_size=64, num_workers=8):
#     print("Extracting all images: ", images)
#     data = torch.utils.data.DataLoader(
#         CLIPImageDataset(images),
#         batch_size=batch_size, num_workers=num_workers, shuffle=False)
#     all_image_features = []
#     with torch.no_grad():
#         for b in data:
#             b = b['image'].to(device)
#             if device == 'cuda':
#                 b = b.to(torch.float16)
#             all_image_features.append(model.encode_image(b).cpu().numpy())
#     all_image_features = np.vstack(all_image_features)
#     return all_image_features

# # %%
# def get_clip_score(images, candidates, w=2.5):
#     '''
#     get standard image-text clipscore.
#     images can either be:
#     - a list of strings specifying filepaths for images
#     - a precomputed, ordered matrix of image features
#     '''
#     if isinstance(images, list):
#         # need to extract image features
#         images = extract_all_images(images, model, device)

#     candidates = extract_all_captions(candidates, model, device)

#     #as of numpy 1.21, normalize doesn't work properly for float16
#     if version.parse(np.__version__) < version.parse('1.21'):
#         images = sklearn.preprocessing.normalize(images, axis=1)
#         candidates = sklearn.preprocessing.normalize(candidates, axis=1)
#     else:
#         warnings.warn(
#             'due to a numerical instability, new numpy normalization is slightly different than paper results. '
#             'to exactly replicate paper results, please use numpy version less than 1.21, e.g., 1.20.3.')
#         images = images / np.sqrt(np.sum(images**2, axis=1, keepdims=True))
#         candidates = candidates / np.sqrt(np.sum(candidates**2, axis=1, keepdims=True))

#     per = w*np.clip(np.sum(images * candidates, axis=1), 0, None)
#     return np.mean(per), per, candidates
