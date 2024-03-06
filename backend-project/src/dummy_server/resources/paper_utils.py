"""
Module Description: 
Util functions to generate claims and link them
"""
import copy
import json
import openai
from nltk.tokenize import sent_tokenize, word_tokenize

openai.api_key = "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"

# pylint: disable=line-too-long
SEGMENTATION_TEMPLATE = \
"""Extract all the claims from a sentence, ignoring extraneous words such as unimportant adverbs. A sentence may contain multiple claims. Each claim should be of the form <subject> <predictate> <object>, and should have the first occurence of any pronouns replaced by their antecedents.

Sentence: "The 3rd and 4th stations all announced that they would be postponed, and the Monaco station was subsequently cancelled."
Claim: Monaco station was cancelled.
Claim: 4th stations announced they would be postponed.
Claim: The 3rd stations announced they would be postponed.
Claim: The 4th stations postponed.
Claim: The 3rd stations postponed.

Sentence: "Lewis Hamilton and Mercedes have once again confirmed themselves as drivers and constructors world champions."
Claim: Mercedes confirmed themselves as constructors world champions.
Claim: Lewis Hamilton confirmed themselves as drivers world champions.

Sentence: "Local organizers in East Palestine, Ohio on Monday said their activism has successfully pressured rail company Norfolk Southern to agree to a limited relocation plan for some residents affected by last month's train derailment, but added they have no intention of backing down from their demand for justice for thousands of people in the area who are struggling in the aftermath of the accident."
Claim: Local organizers said their activism has pressued rail company Norfolk Southern to agree to a limited relocation plan.
Claim: Local organizers have no intention of backing down from their demand for justice.
Claim: Rail company Norfolk Southern agree to a limited relocation plan.

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

def get_sentences(paper):
    """
    Extract the sentences from the paper's paragraphs, and store them.
    """
    sentences = []
    paragraphs = json.loads(paper['annotations']['paragraph'])

    for p in paragraphs:
        paragraph = paper['text'][p['start']:p['end']]
        sentences.extend(sent_tokenize(paragraph))

    paper['sentences'] = sentences
    return paper

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
    prompt = make_prompt(' '.join(sentence.split())),
    completion = openai.completions.create(
        model=model_name,
        prompt=prompt,
        max_tokens=128,
        temperature=0,
    )
    claims = completion.choices[0].text.strip().split('\n')
    claims = [c for c in claims if c[:6] == 'Claim:']
    claims = [c[6:].strip() for c in claims]
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
            key=lambda x: word_overlap_distance(tokenized_claim, x[1]))

        best_match = list(sorted_sentences)[0]

        linked_claims.append({
            'claim': claim,
            'sentence_id': best_match[0],
            'paper_id': paper['id'],
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
