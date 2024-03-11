"""
Module Description: 
Data Scraper from S2ORC: The Semantic Scholar Open Research Corpus. 
https://www.semanticscholar.org/product/api 
"""
import json
from os import remove
from os.path import exists
import requests
from pyspark.sql.functions import lower

# Define the paper search endpoint URL
BASE_URL_PAPER = 'https://api.semanticscholar.org/graph/v1/paper/'
BASE_URL_RECOMMEND = 'https://api.semanticscholar.org/recommendations/v1/papers/forpaper/'
# Define base URL for datasets API
BASE_URL = "https://api.semanticscholar.org/datasets/v1/release/"

# Define the time-out
TIME_OUT = 100

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


def get_paper(keyword: str):
    """
    Data Scraper function to retrieve the data based on the input from users.
    """

    # Define the required query parameter and the limits
    query_params = {
        'query': keyword,
        'limit': 1
    }

    url = BASE_URL_PAPER + 'search'

    # Make the GET request to the paper search endpoint with the URL and query parameters
    search_response = requests.get(url, headers=headers, params=query_params, timeout=TIME_OUT)

    # Check if the request was successful (status code 200)
    if search_response.status_code == 200:
        search_response = search_response.json()

        if 'data' not in search_response.keys():
            return None

        for paper in search_response['data']:
            # Retrieve the paper id corresponding to the result in the list
            paper_id = paper['paperId']

            # Retrieve the paper details corresponding to this paper id using the function we defined earlier.
            paper_detail = get_paper_data(paper_id)

            # Check if paper_details is not None before proceeding
            if paper_detail is not None:
                return paper_detail
            else:
                print("Failed to retrieve paper details.")

    else:
        # Handle potential errors or non-200 responses
        print(f"Relevance Search Request failed with status code {search_response.status_code}: {search_response.text}")

    return None



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

def extract_titles_udf(paper):
    """
    Extract the titles of the papers
    """
    if paper['annotations']['title'] is None:
        return ""
    title_start = int(json.loads(paper['annotations']['title'])[0]['start'])
    title_end = int(json.loads(paper['annotations']['title'])[0]['end'])
    title = paper['text'][title_start: title_end]
    return title

def find_element(search_string, dataframe):
    """
    Find if the collections contain certain paper
    """
    # Convert the string to lowercase
    string_lower = search_string.lower()

    # Filter rows where the column value is equal to the search string
    exact_match = dataframe.filter(lower(dataframe['title']) == string_lower)
    if not exact_match.isEmpty():
        return True, exact_match.head(1)[0]

    # If the string is neither in the list nor a substring of any element
    return False, None

def write_json_to_file(json_obj, file_path):
    """
    Helper function to write a json object to a jsonl file
    """
    # Open the file in append mode ('a')
    with open(file_path, 'a', encoding='utf-8') as jfile:
        # Serialize the JSON object and write it to the file
        json.dump(json_obj, jfile)
        # Add a newline character to separate JSON objects
        jfile.write('\n')


def download_dataset(dataset_name: str):
    """
    Helper function to download the datasets from scholar API
    """
    print("Begin to download ", dataset_name, ".json link ...")
    # Make the initial request to get the list of releases
    response = requests.get(BASE_URL, timeout=TIME_OUT, headers=headers)

    if response.status_code == 200:
        # Assume we want data from the latest release, which will correspond to the last item
        # in the response list since releases are ordered chronologically
        release_id = response.json()[-1]

        # Make a request to get datasets available in the latest release
        datasets_response = requests.get(BASE_URL + release_id, timeout=TIME_OUT, headers=headers)

        if datasets_response.status_code == 200:
            # Fetch the datasets list from the response
            datasets = datasets_response.json()['datasets']

            # Check if the 'papers' dataset exists
            papers_dataset_exists = any(dataset.get('name') == dataset_name for dataset in datasets)

            if papers_dataset_exists:
                # Make a request to get download links for the dataset
                download_links_response = requests.get(BASE_URL + release_id + '/dataset/' + dataset_name,
                                                    headers=headers, timeout=TIME_OUT)
                if download_links_response.status_code == 200:
                    if exists(dataset_name+'.json'):
                        remove(dataset_name+'.json')
                    with open(dataset_name+".json", "w", encoding='utf-8') as json_file:
                        json.dump(download_links_response.json(), json_file, indent=4)
                    print(dataset_name, ".json downloaded done")
                else:
                    print(f"Failed to get link. Status code: {download_links_response.status_code}")
            else:
                print("The 'papers' dataset does not exist in the list.")
        else:
            print(f"Failed to get datasets. Status code: {datasets_response.status_code}")
    else:
        print(f"Failed to get releases. Status code: {response.status_code}")
