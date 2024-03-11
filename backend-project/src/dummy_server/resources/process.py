"""
Module Description: 
"""

import os
import json
import sys
import openai
from tqdm import tqdm
import numpy as np
from dummy_server.resources.filtering import get_sentencepairs, init_embedding_model, get_similarity_scores
from dummy_server.resources.entailment import init_model, classify_nli
from dummy_server.resources.paper_utils import merge_paragraphs, get_sentences, get_claims_from_paragraph, get_claims_from_sentence, link_claims

data_root = os.path.join(".", "data")

print(data_root)

sys.exit()

with open(data_root / 'key.json', encoding='utf-8') as f:
    keys = json.load(f)
    openai.api_key = keys['open-ai']

MODEL_NAME = 'text-davinci-003'

"""
Open the paper file
"""

papers = []
with open(data_root / 'papers.jsonl', encoding='utf-8') as fp:
    for line in fp:
        papers.append(json.loads(json.loads(line.strip())))

paper2claims = {}

for paper in papers:
    if paper['title'] in paper2claims:
        continue

    merged_p = merge_paragraphs(paper['paragraphs'], min_words=100, max_words=1000)
    paper_claims = []
    print([len(p) for p in merged_p])

    for p in merged_p:
        # print(len(p.split()))
        response, claims = get_claims_from_sentence(p, MODEL_NAME)
        reason = response.choices[0]['finish_reason']
        total_text = p + response.choices[0].text

        # pylint: disable=invalid-name
        tries = 0
        while reason != 'stop' or tries > 4:
            print('trying again...')
            response, claims = get_claims_from_sentence(total_text, MODEL_NAME)
            reason = response.choices[0]['finish_reason']
            total_text += response.choices[0].text
            tries = tries + 1

        paper_claims.extend(claims)

        for c in paper_claims:
            print(c)
        print()

    paper2claims[paper['title']] = paper_claims

json.dump(paper2claims, open(data_root / 'paper2claims.json', 'w', encoding='utf-8'))

paper2claims = {}
with open(data_root / 'paper2claims.json', encoding='utf-8') as fp:
    paper2claims = json.load(fp)

for a in papers:
    if a['title'] in paper2claims:
        print('added claims')
        a['openai_claims'] = paper2claims[a['title']]
    else:
        a['openai_claims'] = []

papers = [get_sentences(paper) for paper in tqdm(papers) if paper['title'] in paper2claims]
papers = [get_claims_from_paragraph(paper, method='openai') for paper in tqdm(papers)]
papers = [link_claims(paper) for paper in tqdm(papers)]

sentences, sentence_pairs, sentence2ids = get_sentencepairs(papers)

model = init_embedding_model()
similarity_scores = get_similarity_scores(sentences, model)
most_similar = np.argsort(similarity_scores, axis=1)[:, ::-1]
most_similar = most_similar[:, 1:21]

pairs = []
for i, row in tqdm(enumerate(most_similar)):
    sentence_i = sentences[i]
    for j in row:
        if i == j:
            continue
        sentence_j = sentences[j]
        if all([s in sentence2ids[sentence_j] for s in sentence2ids[sentence_i]]):
            continue
        pairs.append((sentence_i, sentence_j))

nli_tokenizer, nli_model = init_model()
probabilities = classify_nli(pairs, nli_tokenizer, nli_model)
contr_thresh = [x for x in list(sorted(probabilities[:, 0], reverse=True)) if x > .7][:100][-1].item()
entai_thresh = [x for x in list(sorted(probabilities[:, 2], reverse=True)) if x > .7][:100][-1].item()

contradiction_idx = probabilities[:, 0] > contr_thresh
entailment_idx = probabilities[:, 2] > entai_thresh

contradictions = [(p, probabilities[i]) for i, p in enumerate(pairs) if contradiction_idx[i]]
entailments = [(p, probabilities[i]) for i, p in enumerate(pairs) if entailment_idx[i]]
print(f"Contradictions: {len(contradictions)}")
print(f"Entailments: {len(entailments)}")

s2support = {}
s2contradict = {}

for x in sentence2ids:
    sentence2ids[x] = list(sentence2ids[x])

for (p, h), _ in entailments:
    if h not in s2support:
        s2support[h] = []
    s2support[h].append((sentence2ids[p], p))

for (p, h), _ in contradictions:
    if h not in s2contradict:
        s2contradict[h] = []
    s2contradict[h].append((sentence2ids[p], p))

claim2sent = {}
for a in papers:
    for claim in a['claims']:
        if claim['claim'] in claim2sent:
            print("DUPLEX")
        else:
            claim2sent[claim['claim']] = claim['sentence']

for a in papers:
    supports = []
    contras = []
    for claim in a['claims']:
        if claim['claim'] in s2support:
            x = {}
            x['my_claim'] = claim['sentence']
            x['links'] = []
            for link in s2support[claim['claim']]:
                x['links'].append({'their_claim': claim2sent[link[1]], 'source':link[0]})
            supports.append(x)

        if claim['claim'] in s2contradict:
            x = {}
            x['my_claim'] = claim['sentence']
            x['links'] = []
            for link in s2contradict[claim['claim']]:
                x['links'].append({'their_claim': claim2sent[link[1]], 'source':link[0]})
            contras.append(x)

    a['supports'] = supports
    a['contradicts'] = contras

json.dump(papers, open(data_root / 'papers_with_links.json', 'w', encoding='utf-8'))
