"""
Module Description: 
"""

import os
import json
import sys
from pathlib import Path
from os import remove
from os.path import exists
from collections import Counter
import warnings
import torch
from tqdm import tqdm
import numpy as np
from nltk.corpus import stopwords
from transformers import pipeline
from dummy_server.resources.news_utils import GoogleNewsFeedScraper, link_claims, get_sentencepairs
from dummy_server.resources.filtering import (
    init_embedding_model,
    get_similarity_scores
)
from dummy_server.resources.paper_utils import (
    merge_paragraphs,
    has_non_excluded_words,
    get_claims_from_sentence,
    get_sentences,
    get_claims_from_paragraph
)

warnings.filterwarnings("ignore", category=UserWarning)

stops = stopwords.words('english')

#############################
### STEP 1: DOWNLOAD INFO ###
#############################

scraper = GoogleNewsFeedScraper(sys.argv[1], verbose=False, number=30)
scraper.scrape_google_news_feed()
scraper.get_texts()

titles, texts, links, venues, urls = (
    scraper.titles,
    scraper.texts,
    scraper.links,
    scraper.venues,
    scraper.urls
)
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

os.makedirs(os.path.dirname(data_root / article_dir / 'articles.jsonl'), exist_ok=True)

if exists(data_root / article_dir / 'articles.jsonl'):
    remove(data_root / article_dir / 'articles.jsonl')

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

MODEL_NAME = 'gpt-3.5-turbo-instruct'

articles = []
with open(data_root / article_dir / 'articles.jsonl', encoding='utf-8') as fp:
    for line in fp:
        articles.append(json.loads(line.strip()))

article2claims = {}

classifier_fact = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
candidate_labels = ['objective fact', 'subjective opinion']

classifier_topic = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
topic_labels = ['immigration', 'other topic']

summarizer = pipeline("summarization", model="Falconsai/text_summarization")

claim_per_article = []
length_per_article = []

for article in articles:
    if article['title'] in article2claims:
        continue

    print(article['venue'])
    merged_p = merge_paragraphs(article['paragraphs'], min_words=30, max_words=300)
    length_per_article.append(int(np.sum([len(p.split()) for p in article['paragraphs']])))
    article_claims = []
    print([len(p.split()) for p in merged_p])

    for p in merged_p:
        if (len(p.split()) < 20):
            continue
        summary = summarizer(p, min_length = int(len(p.split())/4), max_length = int(len(p.split())/2), do_sample = False)

        response, claims = get_claims_from_sentence(summary[0]['summary_text'], MODEL_NAME)
        reason = response.choices[0].finish_reason
        total_text = p + response.choices[0].text

        # pylint: disable=invalid-name
        tries = 0
        while reason != 'stop' or tries > 4:
            print('trying again...')
            if len(total_text) > 4097:
                break
            response, claims = get_claims_from_sentence(total_text, MODEL_NAME)
            reason = response.choices[0].finish_reason
            total_text += response.choices[0].text
            tries += 1

        article_claims.extend(claims)
    
    article_claims = [article_claim for article_claim in article_claims if has_non_excluded_words(article_claim)]

    fact_labels = classifier_fact(article_claims, candidate_labels, multi_label=False)
    fact_idx = [1 if item['labels'][0] == 'objective fact' and item['scores'][0] > .5 else 0 for item in fact_labels]
    article_claims = [article_claim for i, article_claim in enumerate(article_claims) if fact_idx[i]]

    labels = classifier_fact(article_claims, topic_labels, multi_label=False)
    topic_idx = [1 if item['labels'][0] == topic_labels[0] and item['scores'][0] > .5 else 0 for item in labels]
    article_claims = [article_claim for i, article_claim in enumerate(article_claims) if topic_idx[i]]

    new_list = []
    for c in article_claims:
        if c not in new_list:
            print(c)
            new_list.append(c)
    print()

    article_claims = new_list
    article2claims[article['title']] = article_claims
    claim_per_article.append(len(article_claims))

article2claims_info = {'Average claims per article': float(np.mean(claim_per_article)),
                       'Maximum': int(np.max(claim_per_article)),
                       'Minimum': int(np.min(claim_per_article)),
                       'Variance': float(np.std(claim_per_article)),
                       'Detail': claim_per_article,
                       'Average paragraph length per article': float(np.mean(length_per_article)),
                       'Detailed length': length_per_article,
                       }

article2claims['extraction_info'] = article2claims_info

if exists(data_root / article_dir / 'article2claims.json'):
    remove(data_root / article_dir / 'article2claims.json')

json.dump(article2claims, open(data_root / article_dir / 'article2claims.json',
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

articles = [get_sentences(article) for article in tqdm(articles) if article['title'] in article2claims]
articles = [get_claims_from_paragraph(article, method='openai') for article in tqdm(articles)]
articles = [link_claims(article) for article in tqdm(articles)]

sentences, sentence_pairs, sentence2urls = get_sentencepairs(articles)

model = init_embedding_model()
similarity_scores = get_similarity_scores(sentences, model)
most_similar = np.argsort(similarity_scores, axis=1)[:, ::-1]
most_similar = most_similar[:, 1:21]

pair_sentences = []
pairs = []
for i, row in tqdm(enumerate(most_similar)):
    sentence_i = sentences[i]
    for j in row:
        if i == j:
            continue
        sentence_j = sentences[j]
        if all([s in sentence2urls[sentence_j] for s in sentence2urls[sentence_i]]):
            continue
        pair_sentences.append("[CLS] "+sentence_i+" [SEP] "+sentence_j+" [SEP]")
        pairs.append((sentence_i, sentence_j))

classifier = pipeline("text-classification", model="microsoft/deberta-large-mnli", top_k = None)
probabilities = classifier(pair_sentences)

neutral_scores = []
contradiction_scores = []
entailment_scores = []

for sublist in probabilities:
    neutral_score = next((item['score'] for item in sublist if item['label'] == 'NEUTRAL'), 0)
    contradiction_score = next((item['score'] for item in sublist if item['label'] == 'CONTRADICTION'), 0)
    entailment_score = next((item['score'] for item in sublist if item['label'] == 'ENTAILMENT'), 0)
    neutral_scores.append(neutral_score)
    contradiction_scores.append(contradiction_score)
    entailment_scores.append(entailment_score)

neutral_array = np.array(neutral_scores)
contradiction_array = np.array(contradiction_scores)
entailment_array = np.array(entailment_scores)

probabilities = np.column_stack((contradiction_array, neutral_array, entailment_array))

prob_indices = np.argmax(probabilities, axis=1)

contradictions = [(p, probabilities[i]) for i, p in enumerate(pairs) if prob_indices[i] == 0 and probabilities[i][0] > .6]
entailments = [(p, probabilities[i]) for i, p in enumerate(pairs) if prob_indices[i] == 2 and probabilities[i][2] > .6]

s2support = {}
s2contradict = {}

for x in sentence2urls:
    sentence2urls[x] = list(sentence2urls[x])

for (p, h), probab in entailments:
    if p not in s2support:
        s2support[p] = []
    s2support[p].append((sentence2urls[h], h, probab))

for (p, h), probab in contradictions:
    if p not in s2contradict:
        s2contradict[p] = []
    s2contradict[p].append((sentence2urls[h], h, probab))

claim2sent = {}
for a in articles:
    for claim in a['claims']:
        if claim['claim'] in claim2sent:
            print("DUPLEX")
        else:
            claim2sent[claim['claim']] = claim['sentence']

linking_matrix = np.zeros((len(articles), len(articles)))
links_per_article = []

total_supports = 0
total_contras = 0

for idx, a in enumerate(articles):
    supports = []
    number_of_supports = 0
    contras = []
    number_of_contras = 0
    for claim in a['claims']:
        if claim['claim'] in s2support:
            x = {}
            x['my_sentence'] = claim['sentence']
            x['my_claim'] = claim['claim']
            x['links'] = []
            for link in s2support[claim['claim']]:
                probabilities_dict = {'probability_1': link[2][0].item(),
                                    'probability_2': link[2][1].item(),
                                    'probability_3': link[2][2].item()} if isinstance(link[2], torch.Tensor) else link[2].tolist()
                x['links'].append({'their_claim': link[1], 'their_sentence': claim2sent[link[1]], 'source':link[0], 'probability': probabilities_dict})
                linking_matrix[idx][link[0]] += 1
                number_of_supports += 1
                total_supports += 1
            supports.append(x)
            

        if claim['claim'] in s2contradict:
            x = {}
            x['my_sentence'] = claim['sentence']
            x['my_claim'] = claim['claim']
            x['links'] = []
            for link in s2contradict[claim['claim']]:
                probabilities_dict = {'probability_1': link[2][0].item(),
                                    'probability_2': link[2][1].item(),
                                    'probability_3': link[2][2].item()} if isinstance(link[2], torch.Tensor) else link[2].tolist()
                x['links'].append({'their_claim': link[1],'their_sentence': claim2sent[link[1]], 'source':link[0], 'probability': probabilities_dict})
                linking_matrix[idx][link[0]] += 1
                number_of_contras +=1
                total_contras += 1
            contras.append(x)

    a['supports'] = supports
    a['contradicts'] = contras
    links_per_article.append(number_of_supports + number_of_contras)

if exists(data_root / article_dir / 'articles_with_links.json'):
    remove(data_root / article_dir / 'articles_with_links.json')

articles_with_links_info = {'Average claims per article': float(np.mean(links_per_article)),
                       'Maximum': int(np.max(links_per_article)),
                       'Minimum': int(np.min(links_per_article)),
                       'Variance': float(np.std(links_per_article)),
                       'Detail': links_per_article
                       }

articles.append(articles_with_links_info)

print(f"Contradictions: {total_contras}")
print(f"Entailments: {total_supports}")

print(linking_matrix)

json.dump(articles, open(data_root / article_dir / 'articles_with_links.json', 'w', encoding='utf-8'))


with open(data_root / article_dir /  'articles_with_links.json', encoding='utf-8') as fp:
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

json.dump(new_data, open(data_root / article_dir / 'link_graphs.json', 'w', encoding='utf-8'))

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

json.dump(claims_positions, open(data_root / article_dir / 'claims_positions.json', 'w', encoding='utf-8'))