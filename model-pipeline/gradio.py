from gradio_client import Client

client = Client("abidlabs/whisper-large-v2")  # connecting to a Hugging Face Space
client.predict("test.mp4", api_name="/predict")