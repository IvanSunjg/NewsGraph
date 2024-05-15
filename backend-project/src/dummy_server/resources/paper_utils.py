"""
Module Description: 
Util functions to generate claims and link them
"""
import os
from pathlib import Path
import copy
import json
import spacy
from openai import OpenAI
from nltk.tokenize import sent_tokenize, word_tokenize

script_dir = os.path.dirname(__file__)
target_dir = os.path.abspath(os.path.join(script_dir, '../../..', 'data'))
data_root = Path(target_dir)

with open(data_root / 'key.json', encoding='utf-8') as f:
    keys = json.load(f)
    client = OpenAI(api_key=keys['open-ai'])

# pylint: disable=line-too-long
SEGMENTATION_TEMPLATE = \
"""Please break down the following sentences into independent facts. A sentence may contain multiple facts. Each fact should be of the form <subject> <predictate> <object>.
Sentence: In 1963, Collins became one of the third group of astronauts selected by NASA and he served as the back-up Command Module Pilot for the Gemini 7 mission.
Fact: Collins became an astronaut in 1963.
Fact: Collins served as the back-up Command Module Pilot. 
Fact: Collins served for the Gemini 7 mission.

Sentence: Michael Collins (born October 31, 1930) is a retired American astronaut and test pilot who was the Command Module Pilot for the Apollo 11 mission in 1969.
Fact: Michael Collins was born on October 31, 1930.
Fact: Michael Collins is an American astronaut.
Fact: Michael Collins is a retired astronaut.
Fact: Michael Collins was a test pilot for the Apollo 11 mission.
Fact: Michael Collins was the Command Module Pilot for the Apollo 11 mission.

Sentence: Miassite is a gray, metallic mineral made of rhodium and sulfur and, as Science Alert explains, was identified as a regular superconductor in 2010.
Fact: Miassite is a gray, metallic mineral.
Fact: Miassite is made of rhodium and sulfur.
Fact: Miassite was identified as a regular superconductor in 2020.

Sentence: """

def make_prompt(sentence, template=SEGMENTATION_TEMPLATE):
    """
    Prompt Template
    """
    return f"{template} {sentence}"

def word_overlap_distance(xwords, ywords):
    """
    word_overlap_distance
    """
    xset = set(xwords)
    yset = set(ywords)
    intersection = set.intersection(xset, yset)
    return -(len(intersection) / len(xset))

def get_sentences_abstract(paper):
    """
    Extract the sentences from the paper's paragraphs, and store them for abstract.
    """
    paragraph = paper['abstract']
    paper['sentences'] = sent_tokenize(paragraph)
    return paper

def get_sentences(article):
    """Extract the sentences from the article's paragraphs, and store them.
    """
    sentences = []
    for p in article['paragraphs']:
        sentences.extend(sent_tokenize(p))
    article['sentences'] = sentences
    return article

def get_claims_from_paragraph(paper, method='sentences'):
    """
    Extract the claims from the paper's paragraphs, and store them.
    """
    if method == 'sentences':
        paper['claims'] = paper['sentences']
    elif method == 'openie':
        paper['claims'] = None
    elif method == 'openai':
        paper['claims'] = paper['openai_claims'] if 'openai_claims' in paper else []
    return paper

def get_claims_from_sentence(sentence, model_name):
    """
    Extract the claims from the a sentence.
    """
    prompt = make_prompt(' '.join(sentence.split()))
    completion = client.completions.create(
        model=model_name,
        prompt=prompt,
        max_tokens=198,
        temperature=0
    )
    claims = completion.choices[0].text.strip().split('\n')
    claims = [c for c in claims if c[:5] == 'Fact:']
    claims = [c[5:].strip() for c in claims]
    return completion, claims

# pylint: disable=cell-var-from-loop
def link_claims(paper):
    """
    link the claims together.
    """
    linked_claims = []
    tokenized_sentences = [word_tokenize(s) for s in paper['sentences']]
    for claim in paper['claims']:
        tokenized_claim = word_tokenize(claim)
        sorted_sentences = sorted(
            enumerate(tokenized_sentences),
            key=lambda x: word_overlap_distance(tokenized_claim, x[1])
        )

        best_match = list(sorted_sentences)[0]

        linked_claims.append({
            'claim': claim,
            'sentence_id': best_match[0],
            'paper_id': paper['paperId'],
            'sentence': paper['sentences'][best_match[0]],
        })
    paper['claims'] = linked_claims
    return paper

def merge_paragraphs(paragraphs, min_words, max_words):
    """
    Merge the paragraphs.
    """
    ps = copy.deepcopy(paragraphs)
    while True:
        lens = [len(p.split()) for p in ps]
        merges = [(x+y, i) for i, (x,y) in enumerate(zip(lens, lens[1:])) if x < min_words or y < min_words]
        valid_merges = [(len_, pos_) for len_, pos_ in merges if len_ < max_words]
        if len(valid_merges) == 0:
            break
        _, best_merge = list(sorted(valid_merges))[0]

        joined = ' '.join([ps[best_merge], ps[best_merge + 1]])
        ps = ps[:best_merge] + [joined] + ps[best_merge+2:]

    return ps

def check_proper_noun(sentence):
    """
    To check if the subject of the sentence is a proper noun.
    """
    nlp = spacy.load("en_core_web_sm")
    # Process the sentence using spaCy
    doc = nlp(sentence)

    # Initialize a list to store potential subjects
    potential_subjects = []

    # Find potential subjects of the sentence
    for token in doc:
        if "subj" in token.dep_:
            # Add the token and its subtree to the list of potential subjects
            potential_subjects.append(token.subtree)

    # Check each potential subject for proper nouns
    for subtree in potential_subjects:
        contains_proper_nouns = True
        for word in subtree:
            if word.pos_ != 'PROPN':  # 'PROPN' for proper nouns
                contains_proper_nouns = False
                break
            # if word.ent_type_ == 'PERSON':  # Exclude named entities recognized as people
            #     contains_proper_nouns = False
            #     break
        if contains_proper_nouns:
            return True  # Return True if any potential subject contains only proper nouns

    return False  # Return False if none of the potential subjects contain only proper nouns

def has_non_excluded_words(sentence):
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(sentence)
    excluded_words = ["this", "that", "these", "those", "there"]  # Add pronouns and other words to be excluded
    for token in doc:
        if token.text.lower() in excluded_words or token.pos_ == "PRON":
            return False
    return True