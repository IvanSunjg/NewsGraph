"""
Module Description: 
Util functions to generate claims and link them for news data
"""
import re
import requests
import feedparser
from bs4 import BeautifulSoup
from requests.exceptions import Timeout
from nltk.tokenize import sent_tokenize, word_tokenize


def parse_document(soup):
    """
    parse document
    """
    title = soup.title.text
    paragraphs = [p.text.strip() for p in soup.find_all('p')]
    links = set([l.get('href') for l in soup.find_all('a')])
    return title, paragraphs, links

class GoogleNewsFeedScraper:
    """
    Class description:
    """
    def __init__(self, query, number=None, verbose=False):
        self.query = query
        self.n = number
        self.entries = None
        self.verbose = verbose
        self.titles = []
        self.texts = []
        self.links = []
        self.venues = []
        self.urls = []

    def scrape_google_news_feed(self):
        """
        scrape the google data based on the query.
        """
        rss_url = f'https://news.google.com/rss/search?q={self.query}&hl=en-US&gl=US&ceid=US:en'
        feed = feedparser.parse(rss_url)
        if feed.entries:
            self.entries = feed.entries
        else:
            print("Nothing Found!")

    def get_texts(self):
        """
        Retrieve all the texts based on the Google news feed.
        """
        if self.n is not None:
            self.entries = self.entries[:self.n]
        print(f"Scraping from {len(self.entries)} urls.")
        for entry in self.entries:
            url = entry.link
            self.urls.append(url)
            domains = re.findall('(http.*(com|org))', str(url))
            if len(domains) > 0:
                domain = domains[0][0]
            else:
                continue  
            if self.verbose:
                print(f"Trying: {url}")
            try:
                response = requests.get(url, timeout=5)
            except Timeout:
                if self.verbose:
                    print("Timeout")
                continue
            if response.status_code == 200:
                data = response.content
                soup = BeautifulSoup(data, 'html.parser')
                title_, paragraphs_, links_ = parse_document(soup)
                self.titles.append(title_)
                self.texts.append(paragraphs_)
                self.links.append(links_)
                self.venues.append(domain)
                if self.verbose:
                    print(title_)
            else:
                if self.verbose:
                    print(response.status_code)

def word_overlap_distance(xwords, ywords):
    """
    word_overlap_distance
    """
    xset = set(xwords)
    yset = set(ywords)
    intersection = set.intersection(xset, yset)
    return -(len(intersection) / len(xset))

# pylint: disable=cell-var-from-loop
def link_claims(article):
    """
    link the claims together.
    """
    linked_claims = []
    tokenized_sentences = [word_tokenize(s) for s in article['sentences']]
    for claim in article['claims']:
        tokenized_claim = word_tokenize(claim)
        sorted_sentences = sorted(
            enumerate(tokenized_sentences),
            key=lambda x: word_overlap_distance(tokenized_claim, x[1]))
        best_match = list(sorted_sentences)[0]
        linked_claims.append({
            'claim': claim,
            'sentence_id': best_match[0],
            'article_id': article['id'],
            'sentence': article['sentences'][best_match[0]],
        })
    article['claims'] = linked_claims
    return article

def get_sentencepairs(papers):
    """
    Get sentence pairs from paper collections.
    """
    sentence_pairs = []
    sentences = set([])
    sentence2ids = {}
    for i, p1 in enumerate(papers):
        id1 = p1['id']
        for j, p2 in enumerate(papers):
            id2 = p2['id']
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

if __name__ == "__main__":
    scraper = GoogleNewsFeedScraper('superconductor', verbose=True, number=20)
    scraper.scrape_google_news_feed()
    scraper.get_texts()
