"""
Module Description: 
query dataset
"""

import logging
import json
import sys
import argparse
from os import listdir, remove
from os.path import isfile, join, exists
import gzip
import shutil
from urllib.error import HTTPError
import wget
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, udf
from pyspark.sql.types import StringType
from data_utils import write_json_to_file, download_dataset, get_paper, extract_titles_udf, find_element

parser = argparse.ArgumentParser(description = \
                                'Decide whether we are examining the abstract or the full body.')
parser.add_argument('--short', action='store_true',
                    help='Decide whether we are examining the abstract or the full body.')

args = parser.parse_args()


# Create a formatter
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

# Create a file handler and set the formatter
file_handler = logging.FileHandler("result.log")
file_handler.setFormatter(formatter)

# Create a stream handler and set the formatter
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)

# Configure logging to output to both file and terminal
logging.basicConfig(level=logging.INFO, handlers=[file_handler, stream_handler])


########################################
### STEP 1: SEMANTIC SCHOLAR API KEY ###
########################################

logging.info("Begin to retrieve the API Key of Semantic Scholar ...")

with open('key.json', encoding='utf-8') as f:
    data = json.load(f)
    API_KEY = data['scholar-api']

headers = {"x-api-key": API_KEY}

logging.info("API Key Retrieved")

######################################################
### STEP 2: s2orc.json and papers-id.json retrieve ###
######################################################

download_dataset("paper-ids")
download_dataset("s2orc")

#########################################
### STEP 3: retrieve the paper titles ###
#########################################

logging.info("Begin to retrieve the papers ...")

with open('paper-list.json', encoding='utf-8') as f:
    data = json.load(f)
    papers = data['paper']

paper_no = len(papers)

logging.info("In total, we need to retrieve %d papers", paper_no)
logging.info("")

########################################################################
### STEP 4: Search for the paper and link the sha ids with corpusids ###
########################################################################

if exists("paper-links.jsonl"):
    remove("paper-links.jsonl")

files = [f for f in listdir('source') if isfile(join('source', f))]
if len(files) > 0:
    for file in files:
        remove("source/"+file)

paper_collections = []
paper_already_found = []

for pr in papers:
    p = get_paper(pr)
    if p is not None:
        paper_collections.append(p)
        logging.info("%s successfully found in dataset", pr)
        logging.info("The name in the dataset is: %s", p['title'])
        logging.info("")
    else:
        logging.info("%s can not be found in dataset!!!", pr)
        logging.info("")

with open('paper-ids.json', encoding='utf-8') as f:
    data = json.load(f)
    id_links = data['files']

for iterator, id_link in enumerate(id_links):
    logging.info("Begin to download paper-ids dataset %d", iterator+1)
    wget.download(id_link, out="source")
    logging.info("paper-ids dataset %d downloading done", iterator+1)

    logging.info("Begin to unzip gz file")
    onlyfile = [f for f in listdir('source') if isfile(join('source', f))]
    with gzip.open('source/'+onlyfile[0], 'rb') as f_in:
        with open('source/data.json', 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)

    logging.info("Begin to read json file...")
    spark = SparkSession.builder \
        .appName("Link") \
        .getOrCreate()
    df = spark.read.json("source/data.json")
    logging.info("json file read done...")

    for paper_collection in paper_collections:
        if paper_collection['paperId'] not in paper_already_found:
            result_df = df.filter(df.sha == paper_collection['paperId'])
            if not result_df.isEmpty():
                paper_collection['corpusId'] = result_df.head(1)[0].asDict()['corpusid']
                write_json_to_file(paper_collection, "paper-links.jsonl")
                logging.info("%s has been found in the paper-ids dataset, corpus-id generated.",
                            paper_collection['title'])
                paper_already_found.append(paper_collection['paperId'])
                logging.info("%d papers already found...", len(paper_already_found))

    spark.stop()
    logging.info("paper-ids dataset %d search done. Delete the files...", iterator+1)
    remove("source/data.json")
    remove("source/"+onlyfile[0])
    files = [f for f in listdir('source') if isfile(join('source', f))]
    if len(files) > 0:
        for file in files:
            remove("source/"+file)

    if len(paper_already_found) == paper_no:
        logging.info("All the possible papers has been found in paper-ids! Leaving Step 4...")
        break

if args.short:
    sys.exit()

########################################################
### STEP 5: Download the paper data and search paper ###
########################################################

papers = []
with open('paper-links.jsonl', encoding='utf-8') as fp:
    for line in fp:
        papers.append(json.loads(line.strip()))

with open('s2orc.json', encoding='utf-8') as f:
    data = json.load(f)
    file_links = data['files']

if exists("papers.jsonl"):
    remove("papers.jsonl")

# pylint: disable=invalid-name
paper_id = 0
paper_already_found = []

iterator = 0
while iterator < len(file_links):

    logging.info("Begin to download s2orc dataset %d", iterator+1)
    try:
        wget.download(file_links[iterator], out="source")
    except HTTPError as e:
        logging.info("s2orc dataset links expired... try create a new one.")
        download_dataset("s2orc")
        with open('s2orc.json', encoding='utf-8') as f:
            data = json.load(f)
            file_links = data['files']
        continue
    logging.info("s2orc dataset %d downloading done", iterator+1)

    logging.info("Begin to unzip gz file")
    onlyfile = [f for f in listdir('source') if isfile(join('source', f))]
    with gzip.open('source/'+onlyfile[0], 'rb') as f_in:
        with open('source/data.json', 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)

    logging.info("Begin to read json file...")
    spark = SparkSession.builder \
        .appName("Search") \
        .getOrCreate()
    df = spark.read.json("source/data.json")
    logging.info("json file read done...")

    # Register the UDF
    # Apply the UDF to create a new column 'title' in the PySpark DataFrame
    extract_titles_spark_udf = udf(extract_titles_udf, StringType())
    df = df.withColumn('title', extract_titles_spark_udf(col('content')))

    for p in papers:
        if p['paperId'] not in paper_already_found:
            result_df = df.filter(df.corpusid == p['corpusId'])
            if not result_df.isEmpty():
                paper_dict = result_df.head(1)[0].asDict()
                paper_dict['content'] = result_df.head(1)[0]['content'].asDict()
                paper_dict['info'] = p
                paper_dict['id'] = paper_id
                paper_id += 1
                paper_json = json.dumps(paper_dict)
                write_json_to_file(paper_json, "papers.jsonl")
                paper_already_found.append(p['paperId'])
                logging.info("Paper: %s found by courpusId: %d!! Saved as id: %d",
                            p['title'], p['corpusId'], paper_id)
                logging.info("%d papers already found...", paper_id)

        if p['paperId'] not in paper_already_found:
            found, element = find_element(p['title'], df)
            if found:
                paper_dict = element.asDict()
                paper_dict['content'] = element['content'].asDict()
                paper_dict['id'] = paper_id
                paper_id += 1
                paper_json = json.dumps(paper_dict)
                write_json_to_file(paper_json, "papers.jsonl")
                paper_already_found.append(p['paperId'])
                logging.info("Paper: %s found by title search!! Saved as id: %d",
                            p['title'], paper_id)
                logging.info("Paper courpus id is: %d. However, it is %d in the s3orc dataset!",
                            p['corpusId'], paper_dict['corpusid'])
                logging.info("%d papers already found...", paper_id)

    spark.stop()
    logging.info("s2orc dataset %d search done. Delete the files...", iterator+1)
    remove("source/data.json")
    remove("source/"+onlyfile[0])
    iterator = iterator + 1
    files = [f for f in listdir('source') if isfile(join('source', f))]
    if len(files) > 0:
        for file in files:
            remove("source/"+file)

    if len(paper_already_found) == paper_no:
        logging.info("All the possible papers have been found in s2orc! Programme Ends...")
        break
