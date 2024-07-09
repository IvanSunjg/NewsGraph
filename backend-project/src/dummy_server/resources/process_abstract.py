"""
Module Description: 
"""

import os
import json
from pathlib import Path
from os import remove
from os.path import exists
import torch
from tqdm import tqdm
import numpy as np
from dummy_server.resources.entailment import init_model, classify_nli
from dummy_server.resources.filtering import (
    get_sentencepairs,
    init_embedding_model,
    get_similarity_scores
)
from dummy_server.resources.paper_utils import (
    get_sentences_abstract,
    get_claims_from_paragraph,
    get_claims_from_sentence,
    link_claims
)

script_dir = os.path.dirname(__file__)
target_dir = os.path.abspath(os.path.join(script_dir, '../../..', 'data'))
data_root = Path(target_dir)

with open(data_root / 'key.json', encoding='utf-8') as f:
    keys = json.load(f)

MODEL_NAME = "gpt-3.5-turbo-instruct"

paper_dir = Path('papers/abstract')

"""
Open the paper file
"""

papers = []
with open(data_root / 'paper-links.jsonl', encoding='utf-8') as fp:
    for line in fp:
        papers.append(json.loads(line.strip()))

paper2claims = {}

for paper in papers:
    if paper['title'] in paper2claims or paper['abstract'] is None:
        continue

    paper_claims = []
    response, claims = get_claims_from_sentence(paper['abstract'], MODEL_NAME)
    reason = response.choices[0].finish_reason
    total_text = paper['abstract'] + response.choices[0].text

    # pylint: disable=invalid-name
    tries = 0
    while reason != 'stop' or tries > 4:
        print('trying again...')
        response, claims = get_claims_from_sentence(total_text, MODEL_NAME)
        if len(total_text) > 4097:
            break
        reason = response.choices[0].finish_reason
        total_text += response.choices[0].text
        tries = tries + 1

    paper_claims.extend(claims)

    for c in paper_claims:
        print(c)
    print()

    paper2claims[paper['title']] = paper_claims

os.makedirs(os.path.dirname(data_root / paper_dir / 'paper2claims.json'), exist_ok=True)

if exists(data_root / paper_dir / 'paper2claims.json'):
    remove(data_root / paper_dir / 'paper2claims.json')

json.dump(paper2claims, open(data_root / paper_dir / 'paper2claims.json', 'w', encoding='utf-8'))

paper2claims = {}
with open(data_root / paper_dir / 'paper2claims.json', encoding='utf-8') as fp:
    paper2claims = json.load(fp)

for a in papers:
    if a['title'] in paper2claims:
        print('added claims')
        a['openai_claims'] = paper2claims[a['title']]
    else:
        a['openai_claims'] = []

papers = [get_sentences_abstract(paper) for paper in tqdm(papers) if paper['title'] in paper2claims]
papers = [get_claims_from_paragraph(paper, method='openai') for paper in tqdm(papers)]
papers = [link_claims(paper) for paper in tqdm(papers)]

sentences, sentence_pairs, sentence2ids = get_sentencepairs(papers)

model = init_embedding_model()
similarity_scores = get_similarity_scores(sentences, model)
most_similar = np.argsort(similarity_scores, axis=1)[:, ::-1]
print(most_similar)
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
contr_thresh = [x for x in list(sorted(probabilities[:, 0], reverse=True)) \
                if x > .7][:100][-1].item()
entai_thresh = [x for x in list(sorted(probabilities[:, 2], reverse=True)) \
                if x > .7][:100][-1].item()

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

for (p, h), probab in entailments:
    if h not in s2support:
        s2support[h] = []
    s2support[h].append((sentence2ids[p], p, probab))

for (p, h), probab in contradictions:
    if h not in s2contradict:
        s2contradict[h] = []
    s2contradict[h].append((sentence2ids[p], p, probab))

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
            x['my_sentence'] = claim['sentence']
            x['my_claim'] = claim['claim']
            x['links'] = []
            for link in s2support[claim['claim']]:
                if isinstance(link[2], torch.Tensor):
                    probabilities_dict = {'probability_1': link[2][0].item(),
                                        'probability_2': link[2][1].item(),
                                        'probability_3': link[2][2].item()}
                else:
                    # If it's already a dictionary, use it directly
                    probabilities_dict = link[2]
                x['links'].append({'their_claim': link[1],'their_sentence': claim2sent[link[1]], 'source':link[0], 'probability': probabilities_dict})
            supports.append(x)

        if claim['claim'] in s2contradict:
            x = {}
            x['my_sentence'] = claim['sentence']
            x['my_claim'] = claim['claim']
            x['links'] = []
            for link in s2contradict[claim['claim']]:
                if isinstance(link[2], torch.Tensor):
                    probabilities_dict = {'probability_1': link[2][0].item(),
                                        'probability_2': link[2][1].item(),
                                        'probability_3': link[2][2].item()}
                else:
                    # If it's already a dictionary, use it directly
                    probabilities_dict = link[2]
                x['links'].append({'their_claim': link[1], 'their_sentence': claim2sent[link[1]], 'source':link[0], 'probability': probabilities_dict})
            contras.append(x)

    a['supports'] = supports
    a['contradicts'] = contras

if exists(data_root / paper_dir / 'papers_with_links.json'):
    remove(data_root / paper_dir / 'papers_with_links.json')

json.dump(papers, open(data_root / paper_dir / 'papers_with_links.json', 'w', encoding='utf-8'))

with open(data_root / paper_dir /  'papers_with_links.json', encoding='utf-8') as fp:
    article_claims = json.load(fp)

new_data = {"name":"immigration","children":[]}

i = 0
for idx, claims in enumerate(article_claims):
    if 'claims' not in claims.keys():
        continue
    new_data["children"].append({"name": str(idx), 'children':[]})
    news_claims = claims['claims']
    for claim in news_claims:
        new_data["children"][idx]['children'].append({'name': str(i), 'claim': claim['claim'], 'supports': [], 'contradicts': []})
        i += 1

for idx, claims in enumerate(article_claims):
    if 'supports' not in claims.keys():
        continue
    for support in claims['supports']:
        for children in new_data['children'][idx]['children']:
            if children['claim'] == support['my_claim']:
                for links in support['links']:
                    for child in new_data['children'][links['source'][0]]['children']:
                        if child['claim'] == links['their_claim']:
                            children['supports'].append("immigration."+str(links['source'][0])+"."+child['name'])
    for contras in claims['contradicts']:
        for children in new_data['children'][idx]['children']:
            if children['claim'] == contras['my_claim']:
                for links in contras['links']:
                    for child in new_data['children'][links['source'][0]]['children']:
                        if child['claim'] == links['their_claim']:
                            children['contradicts'].append("immigration."+str(links['source'][0])+"."+child['name'])

json.dump(new_data, open(data_root / paper_dir / 'link_graphs.json', 'w', encoding='utf-8'))

claims_positions = []
for paper in article_claims:
    if 'paragraphs' in paper.keys():
        paragraphs = list(filter(lambda s: s != "", paper['paragraphs']))
        claim_positions = [[] for _ in range(len(paragraphs))]
        for claim in paper['claims']:
            no_support = 0
            no_contras = 0
            for support in paper['supports']:
                if support['my_claim'] == claim['claim']:
                    no_support = len(support['links'])
            for contras in paper['contradicts']:
                if contras['my_claim'] == claim['claim']:
                    no_contras = len(contras['links'])
            for i, paragraph in enumerate(paragraphs):
                if claim['sentence'] in paragraph:
                    claim_positions[i].append({'claim':claim['claim'], 'sentence':claim['sentence'], 'supports':no_support, 'contradicts':no_contras})
        claims_positions.append(claim_positions)

for i, claim_positions in enumerate(claims_positions):
    for claims in claim_positions:
        for claim in claims:
            supports_positions = []
            for support in article_claims[i]['supports']:
                if support['my_claim'] == claim['claim']:
                    for link in support['links']:
                        for j, c_positions in enumerate(claims_positions[link['source'][0]]):
                            for k, c_position in enumerate(c_positions):
                                if(c_position['claim'] == link['their_claim']):
                                    supports_positions.append({"paper_no":link['source'][0],"paragraph":j,"their_claim":link['their_claim']})
            claim["supports_positions"] = supports_positions
            contradicts_positions = []
            for support in article_claims[i]['contradicts']:
                if support['my_claim'] == claim['claim']:
                    for link in support['links']:
                        for j, c_positions in enumerate(claims_positions[link['source'][0]]):
                            for k, c_position in enumerate(c_positions):
                                if(c_position['claim'] == link['their_claim']):
                                    contradicts_positions.append({"paper_no":link['source'][0],"paragraph":j,"their_claim":link['their_claim']})
            claim["contradicts_positions"] = contradicts_positions

json.dump(claims_positions, open(data_root / paper_dir / 'claims_positions.json', 'w', encoding='utf-8'))
