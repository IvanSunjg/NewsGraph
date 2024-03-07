"""
Module Description: 
query dataset
"""

import json
from os import listdir, remove
from os.path import isfile, join, exists
import gzip
import shutil
import requests
import wget
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, udf, lower
from pyspark.sql.types import StringType


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

    # Filter rows where the column value contains the search string as a substring
    substring_match = dataframe.filter(lower(dataframe['title']).contains(string_lower))
    if not substring_match.isEmpty():
        return True, substring_match.head(1)[0]

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

#######################################
### STEP 1: SEMANTIC SCHOLAR API KY ###
#######################################

print("Begin to retrieve the API Key of Semantic Scholar ...")

with open('key.json', encoding='utf-8') as f:
    data = json.load(f)
    API_KEY = data['scholar-api']

headers = {"x-api-key": API_KEY}

print("API Key Retrieved")

###################################
### STEP 2: s2orc.json retrieve ###
###################################

# Define the time-out
TIME_OUT = 10
print("Begin to download s2orc.json link ...")
# Define base URL for datasets API
BASE_URL = "https://api.semanticscholar.org/datasets/v1/release/"
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
        papers_dataset_exists = any(dataset.get('name') == 's2orc' for dataset in datasets)

        if papers_dataset_exists:
            # Make a request to get download links for the 's2orc' dataset
            download_links_response = requests.get(BASE_URL + release_id + '/dataset/s2orc',
                                                   headers=headers, timeout=TIME_OUT)
            if download_links_response.status_code == 200:
                if exists('s2orc.json'):
                    remove('s2orc.json')
                with open("s2orc.json", "w", encoding='utf-8') as json_file:
                    json.dump(download_links_response.json(), json_file, indent=4)
                print("s2orc.json downloaded done")
            else:
                print(f"Failed to get link. Status code: {download_links_response.status_code}")
        else:
            print("The 'papers' dataset does not exist in the list.")
    else:
        print(f"Failed to get datasets. Status code: {datasets_response.status_code}")
else:
    print(f"Failed to get releases. Status code: {response.status_code}")

#########################################
### STEP 3: retrieve the paper titles ###
#########################################

print("Begin to retrieve the papers ...")

with open('paper-list.json', encoding='utf-8') as f:
    data = json.load(f)
    papers = data['paper']

print("In total, we need to retrieve ", len(papers), " papers")

with open('s2orc.json', encoding='utf-8') as f:
    data = json.load(f)
    file_links = data['files']

########################################################
### STEP 4: Download the paper data and search paper ###
########################################################

if exists("papers.jsonl"):
    remove("papers.jsonl")

# pylint: disable=invalid-name
paper_id = 0
paper_already_found = []

for iterator, file_link in enumerate(file_links):

    print("Begin to download dataset ", iterator+1)
    wget.download(file_link, out="source")
    print("Dataset ",  iterator+1, " downloading done")

    print("Begin to unzip gz file")
    onlyfile = [f for f in listdir('source') if isfile(join('source', f))]
    with gzip.open('source/'+onlyfile[0], 'rb') as f_in:
        with open('source/data.json', 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)

    print("Begin to read json file...")
    spark = SparkSession.builder \
        .appName("Search") \
        .getOrCreate()
    df = spark.read.json("source/data.json")
    print("json file read done...")

    # Register the UDF
    # Apply the UDF to create a new column 'title' in the PySpark DataFrame
    extract_titles_spark_udf = udf(extract_titles_udf, StringType())
    df = df.withColumn('title', extract_titles_spark_udf(col('content')))

    for p in papers:
        if p not in paper_already_found:
            found, element = find_element(p, df)
            if found:
                paper_dict = element.asDict()
                paper_dict['content'] = element['content'].asDict()
                paper_dict['id'] = paper_id
                paper_id += 1
                paper_json = json.dumps(paper_dict)
                write_json_to_file(paper_json, "papers.jsonl")
                paper_already_found.append(p)
                print("Paper: ", p, " already found! Saved as id: ", paper_id)

    spark.stop()
    print(paper_id, " papers already found...")
    print("Dataset ", iterator+1, " search done. Delete the files...")
    remove("source/data.json")
    remove("source/"+onlyfile[0])

    if iterator == 0:
        break
