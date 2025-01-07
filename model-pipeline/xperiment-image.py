import requests
from PIL import Image
from io import BytesIO
import torch
from torchvision.transforms import Compose, Resize, CenterCrop, ToTensor, Normalize

from clipscore import get_clip_score

url1 = "https://imagesvc.meredithcorp.io/v3/mm/image?url=https%3A%2F%2Fpublic-assets.meredithcorp.io%2Fe9a8fb98d1ab76b04dc5837f7484b3b6%2F171595023137120240516_164839.jpg&c=sc&poi=face&q=60&orient=true"
url2 = "./test-image/loish.jpg"

response = requests.get(url1)
image = Image.open(BytesIO(response.content))
# image.show()

image = Image.open(url2)
# image.show()

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
        url = self.data[idx]
        # response = requests.get(url)
        # image = Image.open(BytesIO(response.content))
        image = Image.open(url)
        image = self.preprocess(image)
        return {'image': image}

    def __len__(self):
        return len(self.data)

score, per, candidates = get_clip_score([url2], ["a person"])

print(score, per, candidates)