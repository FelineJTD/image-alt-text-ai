# A comparison between several methods for Named Entity Recognition (NER) in Python.

sentence = "Apple is looking at buying U.K. startup for $1 billion"

# Method 1: Using NLTK
import nltk
from nltk.tokenize import word_tokenize
from nltk.tag import pos_tag
from nltk.chunk import ne_chunk

nltk.download('maxent_ne_chunker')
nltk.download('maxent_ne_chunker_tab')
nltk.download('averaged_perceptron_tagger_eng')
nltk.download('words')

nltk_entities = ne_chunk(pos_tag(word_tokenize(sentence)))
print("--- NLTK ---")
print(nltk_entities)


# Method 2: Using spaCy small model (less accurate)
# DATE - absolute or relative dates or periods
# PERSON - People, including fictional
# GPE - Countries, cities, states
# LOC - Non-GPE locations, mountain ranges, bodies of water
# MONEY - Monetary values, including unit
# TIME - Times smaller than a day
# PRODUCT - Objects, vehicles, foods, etc. (not services)
# CARDINAL - Numerals that do not fall under another type
# ORDINAL - "first", "second", etc.
# QUANTITY - Measurements, as of weight or distance
# EVENT - Named hurricanes, battles, wars, sports events, etc.
# FAC - Buildings, airports, highways, bridges, etc.
# LANGUAGE - Any named language
# LAW - Named documents made into laws.
# NORP - Nationalities or religious or political groups
# PERCENT - Percentage, including "%"
# WORK_OF_ART - Titles of books, songs, etc.
import spacy
from collections import Counter

nlp = spacy.load("en_core_web_sm")

doc = nlp(sentence)

print("--- SPACY ---")
spacy_small_entities = doc.ents
print([(X.text, X.label_) for X in doc.ents])
print(Counter([X.label_ for X in doc.ents]))


# Method 3: Using spaCy large model (more accurate)
import spacy
from collections import Counter

nlp = spacy.load("en_core_web_trf")

doc = nlp(sentence)

print("--- SPACY ---")
spacy_transformer_entities = doc.ents
print([(X.text, X.label_) for X in doc.ents])
print(Counter([X.label_ for X in doc.ents]))


# Method 4: Using Flair
from flair.data import Sentence
from flair.models import SequenceTagger

tagger = SequenceTagger.load('ner')

sentence = Sentence(sentence)

tagger.predict(sentence)

print("--- FLAIR ---")
flair_entities = sentence.get_spans('ner')
print(flair_entities)


# Method 5: Using GPT-4o
import openai
import json

def generate_prompt(labels, text):
    prompt = """
    Extract the entities for the following labels from the given text and provide the results in JSON format.
    - Entities must be extracted exactly as mentioned in the text.
    - Return each entity under its label without creating new labels.
    - Provide a list of entities for each label, ensuring that if no entities are found for a label, an empty list is returned.
    - Accuracy and relevance in your responses are key.

    labels:"""

    for label in labels:
        prompt += f"\n- {label}"


    prompt += """
    JSON Structure:
    {
    """

    for label in labels:
        prompt += f'"{label}": [],\n'

    prompt += "}\n\n"
    prompt +="\n\nTEXT:"
    # prompt += text

    print(prompt)
    return prompt

labels = ['SKILLS', 'NAME', 'CERTIFICATE', 'HOBBIES', 'COMPANY', 'UNIVERSITY']

# def gpt_ner(prompt):
#     MODEL="gpt-4o"

#     completion = client.chat.completions.create(
#         model=MODEL,
#         messages=[
#             {"role": "system", "content": "Supreme Entity Recognition Expert"},
#             {"role": "user", "content": prompt}
#         ]
#     )
#     return completion.choices[0].message.content
    
# gpt_entities = gpt_ner(generate_prompt(labels, sentence))


# # Ollama for LLaMA3 and Mixtral
# import ollama
# def ollama_ner(model, text):
#     response = ollama.chat(model=OLLAMA_MODEL, messages=[
#     {
#     'role': 'user',
#     'content': prompt ,
#     },
#     ])
#   return response['message']['content']

# # Sample Text
# text = "......"

# # Results
# gpt_result = gpt_ner(text)
# llama_result = ollama_ner('llama3', text)
# mixtral_result = ollama_ner('mixtral', text)

# print("GPT-4 Result:", gpt_result)
# print("LLaMA3 Result:", llama_result)
# print("Mixtral Result:", mixtral_result)


# Comparison