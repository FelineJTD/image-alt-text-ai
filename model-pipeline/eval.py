import json
import os
import nltk

# Main
if __name__ == "__main__":
    json_dir = "./output-all"

    bleu_scores = []
    # cider_scores = []
    # meteor_scores = []

    filenames = os.listdir(json_dir)

    print(f"Evaluating {len(filenames)} files...")

    # Loop through each JSON file in the directory
    for filename in os.listdir(json_dir):
        if filename.endswith(".json"):
            try:
                # Read the JSON file
                with open(os.path.join(json_dir, filename), "r") as file:
                    data = json.load(file)
                
                for result in data:
                    # Extract the image link and textual context from the JSON data
                    correct_alt_text = result["correct_alt_text"]
                    ai_predicted_alt_text = result["ai_predicted_alt_text"]

                    if (result["ai_predicted_role"] == result["correct_role"]):
                    # if True:

                        bleu_score = nltk.translate.bleu_score.sentence_bleu([correct_alt_text], ai_predicted_alt_text)
                        # cider_score = nltk.translate.cider_score.sentence_cider([correct_alt_text], ai_predicted_alt_text)
                        # meteor_score = nltk.translate.meteor_score.sentence_meteor([correct_alt_text], ai_predicted_alt_text)

                        bleu_scores.append(bleu_score)
                        # cider_scores.append(cider_score)
                        # meteor_scores.append(meteor_score)

                        scores = {
                            "bleu": bleu_score,
                            # "cider": cider_score,
                            # "meteor": meteor_score
                        }

                        # Append the scores to a JSON file
                        with open(f"./output-scores/scores.txt", "a") as file:
                            json.dump(scores, file, indent=4)

            except Exception as e:
                print(str(e))

    print(f"Evaluated {len(bleu_scores)} images.")
    print(f"BLEU scores max: {max(bleu_scores)}")
    print(f"BLEU scores min: {min(bleu_scores)}")
    print(f"BLEU scores mean: {sum(bleu_scores)/len(bleu_scores)}")

    # print(f"CIDEr scores max: {max(cider_scores)}")
    # print(f"CIDEr scores min: {min(cider_scores)}")
    # print(f"CIDEr scores mean: {sum(cider_scores)/len(cider_scores)}")

    # print(f"METEOR scores max: {max(meteor_scores)}")
    # print(f"METEOR scores min: {min(meteor_scores)}")
    # print(f"METEOR scores mean: {sum(meteor_scores)/len(meteor_scores)}")
