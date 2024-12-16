import json
import os
import nltk
from cidereval import cider
from nltk.translate.meteor_score import single_meteor_score
import random

nltk.download('wordnet')


# Main
if __name__ == "__main__":
    json_dir = "./output-FINAL"

    scores = []

    # bleu_scores = []
    # cider_scores = []
    # # meteor_scores = []

    filenames = os.listdir(json_dir)

    print(f"Evaluating {len(filenames)} files...")

    results = {
        "informative": [],
        "functional": [],
        "complex": [],
    }

    # Loop through each JSON file in the directory
    for filename in os.listdir(json_dir):
        if filename.endswith(".json"):
            try:
                # Read the JSON file
                with open(os.path.join(json_dir, filename), "r") as file:
                    data = json.load(file)
                
                for i in range(len(data)):
                    # Extract the image link and textual context from the JSON data
                    correct_alt_text = data[i]["correct_alt_text"]
                    ai_predicted_contextual_alt_text = data[i]["ai_predicted_contextual_alt_text"]
                    ai_predicted_descriptive_alt_text = data[i]["ai_predicted_descriptive_alt_text"]

                    if ((data[i]["ai_predicted_role"] != "decorative") and (data[i]["correct_alt_text"] != "0") and (data[i]["correct_alt_text"] != "-") and (data[i]["correct_alt_text"] != "q")):
                        # print(f"Correct: {correct_alt_text}")
                        # print(f"AI: {ai_predicted_contextual_alt_text}")
                    # if True:

                        results[data[i]["correct_role"]].append({
                            "human": correct_alt_text,
                            "contextual": ai_predicted_contextual_alt_text,
                            "descriptive": ai_predicted_descriptive_alt_text,
                            "img_url": data[i]["input_img_src"],
                            "role": data[i]["correct_role"],
                            "site": filename[:-5]
                        })

                        # bleu1_score_c = nltk.translate.bleu_score.sentence_bleu([correct_alt_text], ai_predicted_contextual_alt_text, weights=(1, 0, 0, 0))
                        # bleu2_score_c = nltk.translate.bleu_score.sentence_bleu([correct_alt_text], ai_predicted_contextual_alt_text, weights=(0.5, 0.5, 0, 0))
                        # bleu3_score_c = nltk.translate.bleu_score.sentence_bleu([correct_alt_text], ai_predicted_contextual_alt_text, weights=(0.33, 0.33, 0.33, 0))
                        # bleu4_score_c = nltk.translate.bleu_score.sentence_bleu([correct_alt_text], ai_predicted_contextual_alt_text, weights=(0.25, 0.25, 0.25, 0.25))

                        # print(f"BLEU-1: {bleu1_score_c}")

                        # cider_score_c = cider(references=[[correct_alt_text]], predictions=[ai_predicted_contextual_alt_text])
                        # print(f"CIDEr: {cider_score_c}")
                        # # cider_score = nltk.translate.cider_score.sentence_cider([correct_alt_text], ai_predicted_alt_text)
                        # # meteor_score = nltk.translate.meteor_score.sentence_meteor([correct_alt_text], ai_predicted_alt_text)

                        # meteor_score_c = single_meteor_score(correct_alt_text.split(), ai_predicted_contextual_alt_text.split())
                        # print(f"METEOR: {meteor_score_c}")

                        # bleu1_score_d = nltk.translate.bleu_score.sentence_bleu([correct_alt_text], ai_predicted_descriptive_alt_text, weights=(1, 0, 0, 0))
                        # bleu2_score_d = nltk.translate.bleu_score.sentence_bleu([correct_alt_text], ai_predicted_descriptive_alt_text, weights=(0.5, 0.5, 0, 0))
                        # bleu3_score_d = nltk.translate.bleu_score.sentence_bleu([correct_alt_text], ai_predicted_descriptive_alt_text, weights=(0.33, 0.33, 0.33, 0))
                        # bleu4_score_d = nltk.translate.bleu_score.sentence_bleu([correct_alt_text], ai_predicted_descriptive_alt_text, weights=(0.25, 0.25, 0.25, 0.25))

                        # print(f"BLEU-1: {bleu1_score_d}")

                        # cider_score_d = cider(references=[[correct_alt_text]], predictions=[ai_predicted_descriptive_alt_text])

                        # print(f"CIDEr: {cider_score_d}")

                        # meteor_score_d = single_meteor_score(correct_alt_text.split(), ai_predicted_descriptive_alt_text.split())


                        # print(f"METEOR: {meteor_score_d}")
                        
                        # # cider_scores.append(cider_score)
                        # # meteor_scores.append(meteor_score)

                        # # scores = {
                        # #     "bleu": bleu_score,
                        # #     # "cider": cider_score,
                        # #     # "meteor": meteor_score
                        # # }

                        # results.append({
                        #     "correct": correct_alt_text,
                        #     "ai": ai_predicted_contextual_alt_text,
                        #     "descriptive": ai_predicted_descriptive_alt_text,
                        #     "img_url": data[i]["input_img_src"],
                        #     "role": data[i]["correct_role"],
                        #     "site": filename[:-5],
                        #     "scores": {
                        #         "contextual": {
                        #             "bleu1": bleu1_score_c,
                        #             "bleu2": bleu2_score_c,
                        #             "bleu3": bleu3_score_c,
                        #             "bleu4": bleu4_score_c,
                        #             "cider": cider_score_c["avg_score"],
                        #             "meteor": meteor_score_c
                        #         },
                        #         "descriptive": {
                        #             "bleu1": bleu1_score_d,
                        #             "bleu2": bleu2_score_d,
                        #             "bleu3": bleu3_score_d,
                        #             "bleu4": bleu4_score_d,
                        #             "cider": cider_score_d["avg_score"],
                        #             "meteor": meteor_score_d
                        #         }
                        #     }
                        # })

            except Exception as e:
                print(str(e))

    # Append the scores to a JSON file
    with open(f"./output-human-data/data.json", "w") as file:
        json.dump(results, file, indent=4)

    # Get 3 random images from each category
    informative = results["informative"]
    functional = results["functional"]
    complex = results["complex"]

    informative_sample = random.sample(informative, 5)
    functional_sample = random.sample(functional, 5)
    complex_sample = random.sample(complex, 5)

    with open(f"./output-human-data/sample.json", "w") as file:
        json.dump({
            "informative": informative_sample,
            "functional": functional_sample,
            "complex": complex_sample
        }, file, indent=4)