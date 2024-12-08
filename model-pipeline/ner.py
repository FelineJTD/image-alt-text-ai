import nltk
from nltk.tokenize import word_tokenize
from nltk.tag import pos_tag
from nltk.chunk import ne_chunk

nltk.download('maxent_ne_chunker')
nltk.download('maxent_ne_chunker_tab')
nltk.download('averaged_perceptron_tagger_eng')
nltk.download('words')

def nltk_ner(text):
    tokenized = ne_chunk(pos_tag(word_tokenize(text)))
    # Format tokenized to JSON
    # {
    #     "CARDINAL": [],
    #     "DATE": [],
    #     "EVENT": [],
    #     "FAC": [],
    #     "GPE": [],
    #     "LANGUAGE": [],
    #     "LAW": [],
    #     "LOC": [],
    #     "MONEY": [],
    #     "NORP": [],
    #     "ORDINAL": [],
    #     "ORG": [],
    #     "PERCENT": [],
    #     "PERSON": [],
    #     "PRODUCT": [],
    #     "QUANTITY": [],
    #     "TIME": [],
    #     "WORK_OF_ART": []
    # }
    entities = {
        "EVENT": [],
        "FAC": [],
        "GPE": [],
        "LAW": [],
        "LOC": [],
        "NORP": [],
        "ORG": [],
        "PERSON": [],
        "PRODUCT": [],
        "WORK_OF_ART": []
    }
    for entity in tokenized:
        if hasattr(entity, 'label') and entity.label() in entities:
            entities[entity.label()].append(entity[0][0])

    # Remove empty lists
    entities = {k: v for k, v in entities.items() if v != []}
    return entities