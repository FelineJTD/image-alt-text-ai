from ner import spacy_ner, gpt_ner
import json
import os
import random
import nltk
from nltk.corpus import stopwords
import time

text = """The French Revolution (French: Révolution française [ʁevɔlysjɔ̃ fʁɑ̃sɛːz]) was a period of political and societal change in France that began with the Estates General of 1789, and ended with the coup of 18 Brumaire in November 1799 and the formation of the French Consulate. Many of its ideas are considered fundamental principles of liberal democracy,[1] while its values and institutions remain central to modern French political discourse.[2]

The causes of the revolution were a combination of social, political, and economic factors which the ancien régime ("old regime") proved unable to manage. A financial crisis and widespread social distress led to the convocation of the Estates General in May 1789, its first meeting since 1614. The representatives of the Third Estate broke away, and re-constituted themselves as a National Assembly in June. The Storming of the Bastille in Paris on 14 July was followed by a series of radical measures by the Assembly, among them the abolition of feudalism, state control over the Catholic Church, and a declaration of rights. The next three years were dominated by the struggle for political control, and military defeats following the outbreak of the French Revolutionary Wars in April 1792 led to an insurrection on 10 August. The monarchy was replaced by the French First Republic in September, and Louis XVI was executed in January 1793.

After another revolt in June 1793, the constitution was suspended, and adequate political power passed from the National Convention to the Committee of Public Safety, led by the Jacobins. About 16,000 people were executed in what was later referred to as Reign of Terror, which ended in July 1794. Weakened by external threats and internal opposition, the Republic was replaced in 1795 by the Directory, and four years later, in 1799, the Consulate seized power in a military coup led by Napoleon Bonaparte on 9 November. This event is generally seen as marking the end of the Revolutionary period. The Revolution resulted from multiple long-term and short-term factors, culminating in a social, economic, financial and political crisis in the late 1780s.[3][4][5] Combined with resistance to reform by the ruling elite, and indecisive policy by Louis XVI and his ministers, the result was a crisis the state was unable to manage.[6][7]

Between 1715 and 1789, the French population grew from 21 to 28 million, 20% of whom lived in towns or cities, Paris alone having over 600,000 inhabitants.[8] This was accompanied by a tripling in the size of the middle class, which comprised almost 10% of the population by 1789.[9] Despite increases in overall prosperity, its benefits were largely restricted to the rentier and mercantile classes, while the living standards fell for wage labourers and peasant farmers who rented their land.[10][11] Economic recession from 1785, combined with bad harvests in 1787 and 1788, led to high unemployment and food prices, causing a financial and political crisis.[3][12][13][14]

While the state also experienced a debt crisis, the level of debt itself was not high compared with Britain's.[15] A significant problem was that tax rates varied widely from one region to another, were often different from the official amounts, and collected inconsistently. Its complexity meant uncertainty over the amount contributed by any authorised tax caused resentment among all taxpayers.[16][a] Attempts to simplify the system were blocked by the regional Parlements which approved financial policy. The resulting impasse led to the calling of the Estates General of 1789, which became radicalised by the struggle for control of public finances.[18]

Louis XVI was willing to consider reforms, but often backed down when faced with opposition from conservative elements within the nobility. Enlightenment critiques of social institutions were widely discussed among the educated French elite. At the same time, the American Revolution and the European revolts of the 1780s inspired public debate on issues such as patriotism, liberty, equality, and democracy. These shaped the response of the educated public to the crisis, [19] while scandals such as the Affair of the Diamond Necklace fuelled widespread anger at the court, nobility, and church officials.[20] """

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


# Clean up the text, removing \n and \t
text = text.replace("\n", " ").replace("\t", " ")

spacy_entities = spacy_ner(text)
print(spacy_entities)

gpt_entities = gpt_ner(text)
print(gpt_entities)


# Compare the results for the two NER models
for label, entities in spacy_entities.items():
    if label in gpt_entities:
        same_count, diff_spacy, diff_gpt = compare_arrays(entities, gpt_entities[label])
        result[label]["common"] += same_count
        result[label]["diff_spacy"] += diff_spacy
        result[label]["diff_gpt"] += diff_gpt

    else:
        print(f"Label: {label}")
        print("No entities found in GPT")
        print("\n")

# Write the results to a file
with open("ner-results-wiki-gpt-4o.json", "w") as f:
    json.dump(result, f, indent=4)

with open(f"output-ner/wiki-gpt-4o.json", "w") as file:
    json.dump({
        "spacy": spacy_entities,
        "gpt": gpt_entities
    }, file, indent=4)

# Calculate the total common, diff_spacy, and diff_gpt
total_common = sum(result[label]["common"] for label in result)
total_diff_spacy = sum(result[label]["diff_spacy"] for label in result)
total_diff_gpt = sum(result[label]["diff_gpt"] for label in result)

print("Total common entities:", total_common)
print("Total different entities (Spacy):", total_diff_spacy)
print("Total different entities (GPT):", total_diff_gpt)
      
