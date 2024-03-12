"""
Module Description: 
"""
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import torch

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

def init_embedding_model():
    """
    Initialise the embedding model.
    """
    embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
    if device is not None:
        embedding_model = embedding_model.to(device)
    return embedding_model

def get_similarity_scores(sentences, embedding_model=None):
    """
    Calculate tge similarity score.
    """
    if embedding_model is None:
        print("embedding model not initialised")
        return -1
    embeddings = embedding_model.encode(sentences)
    similarity_scores = cosine_similarity(embeddings)
    return similarity_scores

def get_sentencepairs(papers):
    """
    Get sentence pairs from paper collections.
    """
    sentence_pairs = []
    sentences = set([])
    sentence2ids = {}
    for i, p1 in enumerate(papers):
        id1 = p1['paperId']
        for j, p2 in enumerate(papers):
            id2 = p2['paperId']
            if i == j:
                continue

            for s1 in p1['claims']:
                c1 = s1['claim']
                if c1 in sentence2ids:
                    sentence2ids[c1].add(id1)
                else:
                    sentence2ids[c1] = set([id1])

                for s2 in p2['claims']:
                    c2 = s2['claim']
                    sentence_pairs.append((c1, c2))
                    sentences.add(c1)
                    sentences.add(c2)

                    if c2 in sentence2ids:
                        sentence2ids[c2].add(id2)
                    else:
                        sentence2ids[c2] = set([id2])

    sentences = [x for x in list(sorted(sentences)) if len(x) > 0]
    return sentences, sentence_pairs, sentence2ids
