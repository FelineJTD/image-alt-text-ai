# import json
# import os
# import nltk
# from cidereval import cider
# from nltk.translate.meteor_score import single_meteor_score

# nltk.download('wordnet')


# # Main
# if __name__ == "__main__":
#     json_dir = "./output-FINAL"

#     scores = []

#     # bleu_scores = []
#     # cider_scores = []
#     # # meteor_scores = []

#     filenames = os.listdir(json_dir)

#     print(f"Evaluating {len(filenames)} files...")

#     results = []

#     # Loop through each JSON file in the directory
#     for filename in os.listdir(json_dir):
#         if filename.endswith(".json"):
#             try:
#                 # Read the JSON file
#                 with open(os.path.join(json_dir, filename), "r") as file:
#                     data = json.load(file)
                
#                 for i in range(len(data)):
#                     # Extract the image link and textual context from the JSON data
#                     correct_alt_text = data[i]["correct_alt_text"]
#                     ai_predicted_contextual_alt_text = data[i]["ai_predicted_contextual_alt_text"]
#                     ai_predicted_descriptive_alt_text = data[i]["ai_predicted_descriptive_alt_text"]

#                     if ( (data[i]["ai_predicted_role"] != "decorative") and (data[i]["correct_alt_text"] != "0") and (data[i]["correct_alt_text"] != "-") and (data[i]["correct_alt_text"] != "q")):
#                         # print(f"Correct: {correct_alt_text}")
#                         # print(f"AI: {ai_predicted_contextual_alt_text}")
#                     # if True:
#                         bleu1_score_c = nltk.translate.bleu_score.sentence_bleu([correct_alt_text], ai_predicted_contextual_alt_text, weights=(1, 0, 0, 0))
#                         bleu2_score_c = nltk.translate.bleu_score.sentence_bleu([correct_alt_text], ai_predicted_contextual_alt_text, weights=(0.5, 0.5, 0, 0))
#                         bleu3_score_c = nltk.translate.bleu_score.sentence_bleu([correct_alt_text], ai_predicted_contextual_alt_text, weights=(0.33, 0.33, 0.33, 0))
#                         bleu4_score_c = nltk.translate.bleu_score.sentence_bleu([correct_alt_text], ai_predicted_contextual_alt_text, weights=(0.25, 0.25, 0.25, 0.25))

#                         print(f"BLEU-1: {bleu1_score_c}")

#                         cider_score_c = cider(references=[[correct_alt_text]], predictions=[ai_predicted_contextual_alt_text])
#                         print(f"CIDEr: {cider_score_c}")
#                         # cider_score = nltk.translate.cider_score.sentence_cider([correct_alt_text], ai_predicted_alt_text)
#                         # meteor_score = nltk.translate.meteor_score.sentence_meteor([correct_alt_text], ai_predicted_alt_text)

#                         meteor_score_c = single_meteor_score(correct_alt_text.split(), ai_predicted_contextual_alt_text.split())
#                         print(f"METEOR: {meteor_score_c}")

#                         bleu1_score_d = nltk.translate.bleu_score.sentence_bleu([correct_alt_text], ai_predicted_descriptive_alt_text, weights=(1, 0, 0, 0))
#                         bleu2_score_d = nltk.translate.bleu_score.sentence_bleu([correct_alt_text], ai_predicted_descriptive_alt_text, weights=(0.5, 0.5, 0, 0))
#                         bleu3_score_d = nltk.translate.bleu_score.sentence_bleu([correct_alt_text], ai_predicted_descriptive_alt_text, weights=(0.33, 0.33, 0.33, 0))
#                         bleu4_score_d = nltk.translate.bleu_score.sentence_bleu([correct_alt_text], ai_predicted_descriptive_alt_text, weights=(0.25, 0.25, 0.25, 0.25))

#                         print(f"BLEU-1: {bleu1_score_d}")

#                         cider_score_d = cider(references=[[correct_alt_text]], predictions=[ai_predicted_descriptive_alt_text])

#                         print(f"CIDEr: {cider_score_d}")

#                         meteor_score_d = single_meteor_score(correct_alt_text.split(), ai_predicted_descriptive_alt_text.split())


#                         print(f"METEOR: {meteor_score_d}")
                        
#                         # cider_scores.append(cider_score)
#                         # meteor_scores.append(meteor_score)

#                         # scores = {
#                         #     "bleu": bleu_score,
#                         #     # "cider": cider_score,
#                         #     # "meteor": meteor_score
#                         # }

#                         results.append({
#                             "correct": correct_alt_text,
#                             "ai": ai_predicted_contextual_alt_text,
#                             "descriptive": ai_predicted_descriptive_alt_text,
#                             "img_url": data[i]["input_img_src"],
#                             "role": data[i]["correct_role"],
#                             "site": filename[:-5],
#                             "scores": {
#                                 "contextual": {
#                                     "bleu1": bleu1_score_c,
#                                     "bleu2": bleu2_score_c,
#                                     "bleu3": bleu3_score_c,
#                                     "bleu4": bleu4_score_c,
#                                     "cider": cider_score_c["avg_score"],
#                                     "meteor": meteor_score_c
#                                 },
#                                 "descriptive": {
#                                     "bleu1": bleu1_score_d,
#                                     "bleu2": bleu2_score_d,
#                                     "bleu3": bleu3_score_d,
#                                     "bleu4": bleu4_score_d,
#                                     "cider": cider_score_d["avg_score"],
#                                     "meteor": meteor_score_d
#                                 }
#                             }
#                         })

#             except Exception as e:
#                 print(str(e))

#     # Append the scores to a JSON file
#     with open(f"./output-FINAL-FIXED-scores/scores.json", "w") as file:
#         json.dump(results, file, indent=4)

#     print("File written: ./output-FINAL-scores/scores.json")

#     bleu1_mean_c = sum([result["scores"]["contextual"]["bleu1"] for result in results]) / len(results)
#     bleu2_mean_c = sum([result["scores"]["contextual"]["bleu2"] for result in results]) / len(results)
#     bleu3_mean_c = sum([result["scores"]["contextual"]["bleu3"] for result in results]) / len(results)
#     bleu4_mean_c = sum([result["scores"]["contextual"]["bleu4"] for result in results]) / len(results)

#     cider_mean_c = sum([result["scores"]["contextual"]["cider"] for result in results]) / len(results)

#     meteor_mean_c = sum([result["scores"]["contextual"]["meteor"] for result in results]) / len(results)

#     print(f"BLEU-1 mean c: {bleu1_mean_c}")
#     print(f"BLEU-2 mean c: {bleu2_mean_c}")
#     print(f"BLEU-3 mean c: {bleu3_mean_c}")
#     print(f"BLEU-4 mean c: {bleu4_mean_c}")

#     print(f"CIDEr mean c: {cider_mean_c}")

#     print(f"METEOR mean c: {meteor_mean_c}")

#     bleu1_mean_d = sum([result["scores"]["descriptive"]["bleu1"] for result in results]) / len(results)
#     bleu2_mean_d = sum([result["scores"]["descriptive"]["bleu2"] for result in results]) / len(results)
#     bleu3_mean_d = sum([result["scores"]["descriptive"]["bleu3"] for result in results]) / len(results)
#     bleu4_mean_d = sum([result["scores"]["descriptive"]["bleu4"] for result in results]) / len(results)

#     cider_mean_d = sum([result["scores"]["descriptive"]["cider"] for result in results]) / len(results)

#     meteor_mean_d = sum([result["scores"]["descriptive"]["meteor"] for result in results]) / len(results)

#     print(f"BLEU-1 mean d: {bleu1_mean_d}")
#     print(f"BLEU-2 mean d: {bleu2_mean_d}")
#     print(f"BLEU-3 mean d: {bleu3_mean_d}")
#     print(f"BLEU-4 mean d: {bleu4_mean_d}")

#     print(f"CIDEr mean d: {cider_mean_d}")

#     print(f"METEOR mean d: {meteor_mean_d}")

