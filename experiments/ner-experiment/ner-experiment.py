from ner import spacy_ner, gpt_ner
import json

text = "The Supreme Court of the United States is the highest court in the federal judiciary of the United States of America. The court consists of the Chief Justice of the United States and eight associate justices who are nominated by the President and confirmed by the Senate. Once appointed, justices have life tenure unless they resign, retire, or are removed after impeachment. In modern discourse, the justices are often categorized as having conservative"

import nltk
from nltk.corpus import stopwords

# Download stopwords (only needs to be done once)
nltk.download('stopwords')

def preprocess_array(array):
    """Remove stopwords and lowercase each element in the array."""
    stop_words = set(stopwords.words('english'))
    
    processed_array = []
    for item in array:
        # Split each element into words
        words = item.split()
        # Remove stopwords and convert to lowercase
        filtered_words = [word.lower() for word in words if word.lower() not in stop_words]
        # Rejoin the filtered words
        processed_array.append(" ".join(filtered_words))
    
    return processed_array

def compare_arrays(array_1, array_2):
    # Convert arrays to sets for efficient comparison
    processed_array_1 = preprocess_array(array_1)
    processed_array_2 = preprocess_array(array_2)

    # Convert arrays to sets for comparison
    set_1 = set(processed_array_1)
    set_2 = set(processed_array_2)
    
    # Calculate intersections (common elements)
    common = set_1.intersection(set_2)
    same_count = len(common)
    
    # Calculate differences
    diff_array_1 = len(set_1 - set_2)  # Elements in set_1 but not in set_2
    diff_array_2 = len(set_2 - set_1)  # Elements in set_2 but not in set_1
    
    return same_count, diff_array_1, diff_array_2

spacy_entities = spacy_ner(text)
print(spacy_entities)

gpt_entities = gpt_ner(text)
print(gpt_entities)

result = {
            "CARDINAL": {"common": 0, "diff_spacy": 0, "diff_gpt": 0},
            "DATE": {"common": 0, "diff_spacy": 0, "diff_gpt": 0},
            "EVENT": {"common": 0, "diff_spacy": 0, "diff_gpt": 0},
            "FAC": {"common": 0, "diff_spacy": 0, "diff_gpt": 0},
            "GPE": {"common": 0, "diff_spacy": 0, "diff_gpt": 0},
            "LANGUAGE": {"common": 0, "diff_spacy": 0, "diff_gpt": 0},
            "LAW": {"common": 0, "diff_spacy": 0, "diff_gpt": 0},
            "LOC": {"common": 0, "diff_spacy": 0, "diff_gpt": 0},
            "MONEY": {"common": 0, "diff_spacy": 0, "diff_gpt": 0},
            "NORP": {"common": 0, "diff_spacy": 0, "diff_gpt": 0},
            "ORDINAL": {"common": 0, "diff_spacy": 0, "diff_gpt": 0},
            "ORG": {"common": 0, "diff_spacy": 0, "diff_gpt": 0},
            "PERCENT": {"common": 0, "diff_spacy": 0, "diff_gpt": 0},
            "PERSON": {"common": 0, "diff_spacy": 0, "diff_gpt": 0},
            "PRODUCT": {"common": 0, "diff_spacy": 0, "diff_gpt": 0},
            "QUANTITY": {"common": 0, "diff_spacy": 0, "diff_gpt": 0},
            "TIME": {"common": 0, "diff_spacy": 0, "diff_gpt": 0},
            "WORK_OF_ART": {"common": 0, "diff_spacy": 0, "diff_gpt": 0}
        }

# Compare the results for the two NER models
for label, entities in spacy_entities.items():
    if label in gpt_entities:
        same_count, diff_spacy, diff_gpt = compare_arrays(entities, gpt_entities[label])
        result[label]["common"] = same_count
        result[label]["diff_spacy"] = diff_spacy
        result[label]["diff_gpt"] = diff_gpt

    else:
        print(f"Label: {label}")
        print("No entities found in GPT")
        print("\n")

# Write the results to a file
with open("ner_results.json", "w") as f:
    json.dump(result, f, indent=4)

# Calculate the total common, diff_spacy, and diff_gpt
total_common = sum(result[label]["common"] for label in result)
total_diff_spacy = sum(result[label]["diff_spacy"] for label in result)
total_diff_gpt = sum(result[label]["diff_gpt"] for label in result)

print("Total common entities:", total_common)
print("Total different entities (Spacy):", total_diff_spacy)
print("Total different entities (GPT):", total_diff_gpt)