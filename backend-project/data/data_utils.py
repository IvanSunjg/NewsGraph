"""
Module Description: 
Data Scraper from S2ORC: The Semantic Scholar Open Research Corpus. 
https://www.semanticscholar.org/product/api 
"""
import json
import requests

# Define the paper search endpoint URL
BASE_URL_PAPER = 'https://api.semanticscholar.org/graph/v1/paper/'
BASE_URL_RECOMMEND = 'https://api.semanticscholar.org/recommendations/v1/papers/forpaper/'

# Define the time-out
TIME_OUT = 10

# API KEY
with open('key.json', encoding='utf-8') as f:
    data = json.load(f)
    API_KEY = data['scholar-api']
headers = {"x-api-key": API_KEY}

def get_paper_data(paper_id: str):
    """
    Define a separate function to make a request to the paper details endpoint using a paper_id.
    This function will be used later on (after we call the paper search endpoint).
    """
    url = BASE_URL_PAPER + paper_id

    # Define which details about the paper you would like to receive in the response
    paper_data_query_params = {'fields': 'title,year,publicationTypes,abstract,authors.name,publicationDate'}

    # Send the API request and store the response in a variable
    response = requests.get(url, headers=headers, params=paper_data_query_params, timeout=TIME_OUT)

    return response.json() if response.status_code == 200 else None

    
def get_papers(keyword: str):
    """
    Data Scraper function to retrieve the data based on the input from users.
    """

    # Define the required query parameter and the limits
    query_params = {
        'query': keyword,
        'limit': 10
    }

    url = BASE_URL_PAPER + 'search'

    paper_collections = []

    # Make the GET request to the paper search endpoint with the URL and query parameters
    search_response = requests.get(url, headers=headers, params=query_params, timeout=TIME_OUT)

    # Check if the request was successful (status code 200)
    if search_response.status_code == 200:
        search_response = search_response.json()

        for paper in search_response['data']:
            # Retrieve the paper id corresponding to the result in the list
            paper_id = paper['paperId']

            # Retrieve the paper details corresponding to this paper id using the function we defined earlier.
            paper_details = get_paper_data(paper_id)

            # Check if paper_details is not None before proceeding
            if paper_details is not None:
                paper_collections.append(paper_details)
            else:
                print("Failed to retrieve paper details.")

    else:
        # Handle potential errors or non-200 responses
        print(f"Relevance Search Request failed with status code {search_response.status_code}: {search_response.text}")
    return paper_collections


def get_recommendations(paper_id: str):
    """
    Retrieving Paper Recommendations.
    """

    url = BASE_URL_RECOMMEND + paper_id

    # Send a GET request to the URL
    response = requests.get(url, headers=headers, timeout=TIME_OUT)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the JSON response
        datas = response.json()

        # Extract the list of recommended papers from the response
        recommended_papers = datas.get("recommendedPapers", [])

    else:
        # Handle the error, e.g., print an error message
        print(f"Request failed with status code {response.status_code}")

    return recommended_papers
