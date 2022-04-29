# Understanding r/antiwork: just another subreddit or a modern labour movement?

This is an accompanying code repository to the Computational Social Science course project. Our report covering key findings is available in this repository, under `/doc` folder.

## Abstract

Reddit's r/antiwork is a subreddit dedicated to exploring ideas about work-free life and finding help related to job struggles which exploded in popularity in 2021. We use a variety of techniques to understand the nature of r/antiwork discussions, user interaction dynamics and broader user participation on Reddit to shed light into the overall community of r/antiwork and understand whether it really represents a beginning of new workers' rights movement as some speculate.

## Directory structure
```
├── LICENSE
├── README.md
├── data -> various extracts of data / images / etc
│   ├── LDA_images -> example topic models
│   ├── ids -> original submission IDs and associated medata data
│   ├── labeled_data -> annotated data used for post archetype analysis
│   ├── submissions -> all filtered/unfiltered posts
│   ├── tests -> test files for OCR/other methods
│   └── users -> summarized versions of user-level datasets
└── src
    ├── data-collection-processing -> data collection and pre-processing scripts
    ├── other-subreddits -> analysis related to other subreddits r/antiwork users participate in
    ├── post-archetypes -> analysis related to classifying posts into post archetypes
    ├── topic-modelling -> analysis related to r\antiwork post topic modelling
    ├── user-networks -> analysis related to user network clusters and connectedness
    └── user-popularity -> analysis related to post popularity given user atttributes
```

## Reproducing our work

### Environment setup

To reproduce steps associated with topic analysis, make sure to use the `env.yml` file to recreate the conda environment. If you are reproducing steps associated with user data collection and analysis, additionally install the packages listed in `requirements.txt`.

### Reproducing data collection

 1. Ensure your Reddit API credentials are available in (https://asyncpraw.readthedocs.io/en/stable/getting_started/configuration/prawini.html?highlight=praw.ini)[praw.ini file], a sample of which is provided in the root folder of the repository.
 2. To reproduce the collection of submission IDs, run notebook `src/topic-modelling/PushShiftAPI.ipynb`. Alternatively, the submission IDs are also in this repository, under `data/ids`.
 3. To reproduce the collection of user-level interactions, run `python src/data-collection-processing/user-data/01. user-info-runner.py` with root directory as the working directory. Note that this process took 3 days on 3 VM's running on parallel. In case you choose to re-collect this data, the following notebooks should be run afterwards:
    1. `src/data-collection-processing/user-data/01b. total_interaction_stats.ipynb` - estimates total interaction counts.
    2. `src/data-collection-processing/user-data/02 user-stat-calculation.ipynb` - produces user-level statistics that are saved to SQLite DB at `data/users/users.sqlite.db`.
    3. `src/data-collection-processing/user-data/03. descriptive_user_stats.ipynb` - updates SQLite DB at `data/users/users.sqlite.db` with additional calculated statistics and produces overall descriptive statistics for the report.
    4. `src/data-collection-processing/user-data/04. adjacency-matrices.ipynb` - creates adjacency matrices used for downstream analysis tasks.
 4. To reproduce the collection of additional metadata required for user popularity regressions, run `python src/data-collection-processing/user-data/05. runner-post-metadata.py` with root directory as the working directory. Notebook `src/data-collection-processing/user-data/06. user-stat-calculation-cutoff.ipynb` should be run afterwards to create the `users_cutoff` table in the SQLite database.

As an alternative, we provide the following downloads for convenience:
 - Raw interaction data produced by step #2 above (to be stored in `data/users/raw/`) (all associated post-processing notebooks still need to be run): https://aurimasazure.blob.core.windows.net/css/raw-user-files.tar.gz (33GB)
 - Raw metadata data produced by step #3 above (to be stored in `data/users/recent`) (associated notebook needs to be run): https://aurimasazure.blob.core.windows.net/css/recent-user-files.tar.gz (114KB)
 - Fully up-to-date SQlite DB and adjacency matrices that allows skipping all data pre-processing steps and focusing on reproducing/extending user analysis (to be stored in `data/users/`): https://aurimasazure.blob.core.windows.net/css/users.tar.gz (133MB)


### Reproducing the analysis

#### Text analysis
 - To reproduce the Preprocessing steps for LDA topic modeling run `src/topic-modeling/Preprocessing.ipynb`
 - To reproduce LDA topic modeling on any labeled data, run `src/topic-modeling/LDA.ipynb`
 - To reproduce the weighted and unweighted sampling of post data to label, run `src/topic-modeling/Sampling_Labeling.ipynb`
 - To reproduce post archetype classifications (Random Forest, Logistic Regression, SVM, BERT finetune, BERT binary finetune), run `src/post-archetypes/Archetype_Analysis.ipynb`

#### User analysis
 - To reproduce the spectral clustering analysis based on user interactions, run `src/user-networks/01.clusters - direct.ipynb`  (direct interactions) and `src/user-networks/02.clusters - indirect.ipynb` (indirect interactions), respectively.
 - To reproduce the connectedness analysis based on pagerank, run `src/user-networks/03.connectedness - direct.ipynb` and `src/user-networks/04.connectedness - indirect.ipynb`, respectively.
 - To reproduce the chart on relationships between topics and users, run `src/user-networks/05.topic_user_relationships.ipynb`
 - To reproduce the user popularity analysis, run `src/user-popularity/user_influence_regressions.ipynb`

If you are using the the SQLite DB we provide, the order of notebooks are run does not matter. If you are re-creating analysis from scratch, note that there are dependencies in how the notebooks should be run (please follow the order above and ensure that you have also replicated the topic analysis / have the necessary files included in the repository). 

#### User participation in other subreddits

- To reproduce data collection related to other subreddits, run notebooks `src/other-subreddits/Reddit_UComment_Subs.ipynb` and `src/other-subreddits/Reddit_UPost_Subs.ipynb` while the user_stats.csv are in the same folder.
- To reproduce associated regression analysis, run notebook `src/other-subreddits/Subreddit Analysis.ipynb` with user_stats.csv, user_posts_subreddits.csv, and user_comments_subreddits.csv
- 'src/other-subreddits/Post Statistics.ipynb' was used for the midterm report and not utilized in the final.

## Authors

Albert Lu, Aurimas Racas, Lawton Walker
