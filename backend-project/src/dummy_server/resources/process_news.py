"""
Module Description: 
"""

import os
import json
import sys
from pathlib import Path
from collections import Counter
import openai
from tqdm import tqdm
import numpy as np
from nltk.corpus import stopwords
from dummy_server.resources.entailment import init_model, classify_nli
from dummy_server.resources.news_utils import get_google_story
from dummy_server.resources.filtering import (
    get_sentencepairs,
    init_embedding_model,
    get_similarity_scores
)
from dummy_server.resources.paper_utils import (
    merge_paragraphs,
    get_claims_from_sentence,
    get_sentences,
    get_claims_from_paragraph,
    link_claims
)

stops = stopwords.words('english')
url = sys.argv[1]

#############################
### STEP 1: DOWNLOAD INFO ###
#############################

titles, texts, links, venues, urls = get_google_story(url, n=20)

indices_of_substantial = [i for i,text in enumerate(texts) if len(text) > 10]

titles_ = [titles[i] for i in indices_of_substantial]
texts_ = [texts[i] for i in indices_of_substantial]
links_ = [links[i] for i in indices_of_substantial]
venues_ = [venues[i] for i in indices_of_substantial]
urls_ = [urls[i] for i in indices_of_substantial]

title_tokens = []
for t in titles_:
    toks = t.lower().split()
    words = []
    for tok in toks:
        if tok in stops:
            continue
        # pylint: disable=invalid-name
        w = ""
        for c in tok:
            if c.isalnum():
                w += c
        if len(w) > 0:
            words.append(w)
    title_tokens.extend(words)

histogram = Counter(title_tokens)
ranked = sorted(histogram, key=lambda x: histogram[x], reverse=True)
MERGED_TITLE = '_'.join(ranked[:5])
print("Save title: ", MERGED_TITLE)

script_dir = os.path.dirname(__file__)
target_dir = os.path.abspath(os.path.join(script_dir, '../../..', 'data'))
data_root = Path(target_dir)

article_dir = Path(f'articles/{MERGED_TITLE}')

with open(data_root / article_dir / 'articles.jsonl', 'w', encoding='utf-8') as fp:
    for i, title in enumerate(titles_):
        obj = {
            'title': title,
            'url': urls_[i],
            'text': ' '.join(texts_[i]),
            'paragraphs': texts_[i],
            'links': list(links_[i]),
            'venue': venues_[i]
        }
        fp.write(f"{json.dumps(obj)}\n")

############################
### STEP 2: SEGMENT TEXT ###
############################

with open(data_root / 'key.json', encoding='utf-8') as f:
    keys = json.load(f)

MODEL_NAME = 'gpt-3.5-turbo-0125'

articles = []
with open(data_root / article_dir / 'articles.jsonl', encoding='utf-8') as fp:
    for line in fp:
        articles.append(json.loads(line.strip()))

article2claims = {}

for article in articles:
    if article['title'] in article2claims:
        continue

    print(article['venue'])
    merged_p = merge_paragraphs(article['paragraphs'], min_words=100, max_words=1000)
    article_claims = []
    print([len(p) for p in merged_p])

    for p in merged_p:
        print(len(p.split()))
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
            tries += 1

        article_claims.extend(claims)

    for c in article_claims:
        print(c)
    print()

    article2claims[article['title']] = article_claims

json.dump(article2claims, open(data_root / article_dir / 'paper2claims.json',
                            'w', encoding='utf-8'))

articles = []

with open(data_root / article_dir / 'articles.jsonl', encoding='utf-8') as fp:
    for i, line in enumerate(fp):
        obj = json.loads(line)
        obj['id'] = i
        articles.append(obj)

article2claims = {}

with open(data_root / article_dir / 'article2claims.json', encoding='utf-8') as fp:
    article2claims = json.load(fp)

for a in articles:
    if a['title'] in article2claims:
        print('added claims')
        a['openai_claims'] = article2claims[a['title']]
    else:
        a['openai_claims'] = []

articles = [get_sentences(article) for article in tqdm(articles) \
            if article['title'] in article2claims]
articles = [get_claims_from_paragraph(article, method='openai') for article in tqdm(articles)]
articles = [link_claims(article) for article in tqdm(articles)]

sentences, sentence_pairs, sentence2urls = get_sentencepairs(articles)

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
        if all([s in sentence2urls[sentence_j] for s in sentence2urls[sentence_i]]):
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

for x in sentence2urls:
    sentence2urls[x] = list(sentence2urls[x])

for (p, h), _ in entailments:
    if h not in s2support:
        s2support[h] = []
    s2support[h].append((sentence2urls[p], p))

for (p, h), _ in contradictions:
    if h not in s2contradict:
        s2contradict[h] = []
    s2contradict[h].append((sentence2urls[p], p))

claim2sent = {}
for a in articles:
    for claim in a['claims']:
        if claim['claim'] in claim2sent:
            print("DUPLEX")
        else:
            claim2sent[claim['claim']] = claim['sentence']

for a in articles:
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

json.dump(articles, open(data_root / article_dir / 'articles_with_links.json',
                        'w', encoding='utf-8'))
