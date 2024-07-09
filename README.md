# NewsGraph

### A Novel Visualization Approach on Robust Facts Inference

LLM's backend part of the work is based on [News Sense](https://github.com/jmilbauer/NewsSense). 

## Project Description 

The exponential proliferation and politicization of news articles pose significant challenges for news readers and journalists in staying informed about real developments ([Benkler et al., 2018](https://academic.oup.com/book/26406?login=false); [Faris et al., 2017](https://dash.harvard.edu/handle/1/33759251)). While collecting articles on common events, traditional news aggregation engines like [Google News](https://news.google.com/home?hl=en-US&gl=US&ceid=US:en) and [ProPublica](https://www.propublica.org/) display them in exhaustive lists, necessitating users to individually read and compare each article ([Milbauer et al., 2023](https://aclanthology.org/2023.emnlp-demo.39/)). Existing solutions often rely on potentially biased third-party designations or static verified fact corpora that struggle to keep pace with rapidly changing facts ([Bondielli & Marcelloni, 2019](https://doi.org/10.1016/j.ins.2019.05.035); [Thorne et al., 2018](https://doi.org/10.18653/v1/n18-1074)). In response to these challenges, we propose the development of an interactive and intelligent reading interface, NewsGraph, designed to enhance users' engagement with news articles and mitigate inherent biases. Building on the framework of NEWSSENSE ([Milbauer et al., 2023](https://aclanthology.org/2023.emnlp-demo.39/)), our interface visualizes results through an interactive dashboard that provides a comprehensive overview of document collections and detailed claim relations. Users can examine the number and influence of claims within documents and navigate clear links between documents to access corresponding claims. 

## Interactive Dashboard

The dashboard comprises several interactive components designed to facilitate user exploration. These include the App Bar, Links Graph, News Comparison, and Frequently Asked Questions (FAQ) sections.

<iframe width="560" height="315" src="https://www.youtube.com/embed/Ue2LL9ghSh8" frameborder="0" allowfullscreen></iframe>

## Requirements

### BackEnd and Data

`cd to the backend-project and follow the instructions(md) inside`.

#### Google News

Folder `/backend-project/data/articles/template` contains an example of data which allows you to try the dashboard directly. It contains the searching results from `Trump administration Immigration` from [Google News](https://news.google.com/search?q=Trump%20administration%20Immigration&hl=en-US&gl=US&ceid=US%3Aen). 

You can also create your own data. You need to create an API Key from [openAI](https://help.openai.com/en/articles/4936850-where-do-i-find-my-openai-api-key). After you get your API Key and have available quota, create a fine named `/backend-project/data/key.json` and make the json file look like this:

```json
{
    "open-ai" : "your openAI API key",
    "scholar-api" : "your semantc scholar API key"
}
```

Substitute `"your openAI API key"` with your real key. `"scholar-api"` is used for ***Research Articles*** analysis. If you only want to play with news articles, you can ignore this key.

Go to `backend-project` and create propoer python environment. `cd to the /backend-project/src/dummy_server/resources` and type:

```python
python process_news.py your_topic_of_interst
```

You should finally get a folder in `/backend-project/data/articles/`. Change its name to `template` and now you should be able to see your results if you start the frontEnd.

#### Research Articles

In principal, the data can be any scraped data from Google News. We also provide an alternative pipeline to analyze the ***Research Articles*** with the help of [Semenatic Scholar](https://www.semanticscholar.org/product/api). Current pipeline only tries to analyze the abstracts. Go to the `/backend-project/data/paper-list.json` and type in the list of paper you are interested in. Also don't forget to add the API key from [Semenatic Scholar](https://www.semanticscholar.org/product/api) and put it in `/backend-project/data/key.json`.

Go to `backend-project` and create propoer python environment. `cd to the /backend-project/src/dummy_server/resources` and type:

```python
python process_abstract.py
```

You should finally get a folder in `/backend-project/data/papers/`. Change its name to `template` and move it to `/backend-project/data/articles/`. Now you should be able to see your results if you start the frontEnd.

**NB**: This pipeline, given the fact that Semantic Scholar API is still in the progress of improvement and papers are usually more complex, is not guaranteed to give robust results. If you are interested to make it better, please contact me :).

### FrontEnd

`cd to the react-frontend and follow the instructions(md) inside`.
