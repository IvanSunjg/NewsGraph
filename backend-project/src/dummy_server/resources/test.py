# import numpy as np
# import json
# Use a pipeline as a high-level helper
from transformers import pipeline

# pipe = pipeline("text-classification", model="microsoft/deberta-large-mnli", top_k = None)
# # # classifier = pipeline("text-classification", model = "roberta-large-mnli", top_k = None)

# probabilities = pipe(['[CLS] Up to $8.1 billion will become available to build the border wall. [SEP] A wall was built along the southern U.S.-Mexico border. [SEP]'])

# print(probabilities)

# # probabilities = classifier(['Hartwig has a co-appointment at the PSFC. Parzyck works at the University of North Texas.',
# #                   'Navrotsky is at Arizona State University. Argonne National Laboratory is located in the United States.',
# #                   'Roberta is a heavily optimized version of BERT. Roberta is not very optimized.',
# #                   'ACT is an organization. NASA is responsible for the civilian space program.',
# #                   'Ibtisam joined AzoNetwork as a freelancer. HTSI is a company.',
# #                   'YBCO is often paired with a ferromagnet (FM). Miassite is typically found as an inclusion.',
# #                   'Azthena may occasionally provide inaccurate responses. Kit Chapman reports on claims.',
# #                   'A scientist says AI could kill us in about 200 years. Ranga Dias claimed to have discovered a superconductor capable of working at room temperature.',
# #                   'HTSI is an innovation leader in the field of high-temperature superconducting tape. Miassite was identified as a regular superconductor in 2010.'])

# # print(probabilities)
# # print()

# # neutral_scores = []
# # contradiction_scores = []
# # entailment_scores = []

# # for sublist in probabilities:
# #     neutral_score = next((item['score'] for item in sublist if item['label'] == 'NEUTRAL'), 0)
# #     contradiction_score = next((item['score'] for item in sublist if item['label'] == 'CONTRADICTION'), 0)
# #     entailment_score = next((item['score'] for item in sublist if item['label'] == 'ENTAILMENT'), 0)
# #     neutral_scores.append(neutral_score)
# #     contradiction_scores.append(contradiction_score)
# #     entailment_scores.append(entailment_score)

# # # Convert lists to NumPy arrays
# # neutral_array = np.array(neutral_scores)
# # contradiction_array = np.array(contradiction_scores)
# # entailment_array = np.array(entailment_scores)

# # # Stack arrays horizontally to create N*3 array
# # result_array = np.column_stack((contradiction_array, neutral_array, entailment_array))

# # print(result_array)

classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
candidate_labels = ['immigration', 'other topic']
sequence_to_classify = ["one day I will see the world.", 
                        "HTSI is an innovation leader in the field of high-temperature superconducting tape.",
                        "AI could kill us in about 200 years or just poses a great potential threat to our future.",
                        "301,000 migrants were paroled at official ports of entry in fiscal 20."]

labels = classifier(sequence_to_classify, candidate_labels, multi_label=False)

results = [1 if item['labels'][0] == 'immigration' and item['scores'][0] > .5 else 0 for item in labels]
print(labels)
print()
print(results)

# claim_per_article = [1,2,3,4,5,6,7,8,9,8,5]


# article2claims_info = {'Average claims per article': float(np.mean(claim_per_article)),
#                        'Maximum': int(np.max(claim_per_article)),
#                        'Minimum': int(np.min(claim_per_article)),
#                        'Variance': float(np.std(claim_per_article))
#                        }
# article2claims = {}
# article2claims['extraction_info'] = article2claims_info

# json_data = json.dumps(article2claims_info)

# # print(json_data)

# # Initialize a N*N zero matrix
# N = 5  # Change N to the desired size
# zero_matrix = np.zeros((N, N))

# zero_matrix[1][2] += 1

# # print(zero_matrix)

# arr = np.array(
# [[ 0. , 0. , 2. , 0. , 0. , 0. , 0. , 0. , 0. , 0. , 0. , 0. , 1. , 1. , 0. , 0. , 0.],
#  [ 0. , 0. , 0. , 0. , 0. , 0. , 0. , 0. , 0. , 1. , 0. , 0. , 2. , 0. , 0. , 1. , 1.],
#  [ 3. , 0. , 0. , 0. , 1. , 1. , 0. , 0. , 0. , 0. , 0. , 0. , 3. , 1. , 0. , 0. , 0.],
#  [ 0. , 0. , 0. , 0. , 0. , 0. , 0. , 0. , 0. , 0. , 0. , 0. , 2. , 0. , 0. , 0. , 0.],
#  [ 0. , 0. , 0. , 0. , 0. , 0. , 0. , 0. , 0. , 2. , 0. , 0. , 1. , 0. , 0. , 1. , 0.],
#  [ 0. , 0. , 0. , 0. , 0. , 0. , 1. , 0. , 0. , 1. , 0. , 0. , 3. , 0. , 0. , 1. , 1.],
#  [ 0. , 0. , 0. , 1. , 0. , 0. , 0. , 0. , 1. , 0. , 1. , 0. , 2. , 0. , 0. , 2. , 0.],
#  [ 0. , 0. , 0. , 1. , 0. , 0. , 0. , 0. , 0. , 0. , 0. , 0. , 1. , 0. , 0. , 2. , 0.],
#  [ 0. , 0. , 0. , 0. , 0. , 0. , 1. , 0. , 0. , 0. , 0. , 2. , 3. , 6. , 0. , 2. , 0.],
#  [ 0. , 2. , 2. , 0. , 2. , 0. , 0. , 0. , 0. , 0. , 1. , 1. , 0. , 0. , 0. , 2. , 17.],
#  [ 0. , 0. , 0. , 1. , 1. , 0. , 1. , 0. , 0. , 1. , 0. , 0. , 7. , 1. , 0. , 1. , 0.],
#  [ 0. , 0. , 0. , 0. , 0. , 0. , 0. , 0. , 1. , 0. , 0. , 0. , 0. , 3. , 0. , 0. , 0.],
#  [ 0. , 1. , 0. , 1. , 0. , 1. , 2. , 0. , 0. , 0. , 3. , 0. , 0. , 0. , 0. , 3. , 0.],
#  [ 1. , 0. , 1. , 0. , 1. , 0. , 0. , 0. , 0. , 0. , 2. , 0. , 3. , 0. , 0. , 1. , 0.],
#  [ 0. , 0. , 1. , 0. , 0. , 0. , 0. , 0. , 1. , 0. , 1. , 0. , 1. , 0. , 0. , 0. , 0.],
#  [ 0. , 1. , 0. , 0. , 0. , 0. , 0. , 0. , 3. , 0. , 1. , 0. , 1. , 0. , 0. , 0. , 1.],
#  [ 0. , 0. , 0. , 0. , 0. , 1. , 0. , 0. , 0. , 1. , 0. , 0. , 0. , 0. , 0. , 0. , 0.]
# ])

# print(np.sum(arr))

# import re

# # Example string
# text = "This is a sample sentence. It contains multiple sentences. Splitting them based on periods."

# # Split the string based on periods while keeping the punctuation
# sentences = re.split(r'(?<=\.) ', text)

# print(sentences)

