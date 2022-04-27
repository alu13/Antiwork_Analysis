# Understanding r/antiwork: just another subreddit or a modern labour movement?

[TBD]

# Directory structure
```
├── LICENSE
├── README.md
├── data -> various extracts of data / images / etc
│   ├── LDA_images
│   ├── ids -> original submission IDs and associated medata data
│   ├── labeled_data -> annotated data used for post archetype analysis
│   ├── submissions -> ?
│   ├── tests -> ?
│   └── users -> summarized versions of user-level datasets
└── src
    ├── data-collection-processing -> data collection and pre-processing scripts
    ├── other-subreddits -> analysis related to other subreddits r/antiwork users participate in
    ├── post-archetypes -> analysis related to classifying posts into post archetypes
    ├── topic-modelling -> analysis related to r\antiwork post topic modelling
    ├── user-networks -> analysis related to user network clusters and connectedness
    └── user-popularity -> analysis related to post popularity given user atttributes
```

# Reproducing our work

## Reproducing data collection

### Scraping of information from Reddit

 0. Ensure your Reddit API credentials are available in (https://asyncpraw.readthedocs.io/en/stable/getting_started/configuration/prawini.html?highlight=praw.ini)[praw.ini file], a sample of which is provided in the root folder of the repository.
 1. To reproduce the collection of submission IDs, run notebook `src/topic-modelling/PushShiftAPI.ipynb`. Alternatively, the submission IDs are also in this repository, under `data/ids`.
 2. To reproduce the collection of user-level interactions, run `python src/data-collection-processing/user-data/01. user-info-runner.py` with root directory as the working directory. Note that this process took 3 days on 3 VM's running on parallel. In case you choose to re-collect this data, the following notebooks should be run afterwards:
    1. `src/data-collection-processing/user-data/01b. total_interaction_stats.ipynb` - estimates total interaction counts.
    2. `src/data-collection-processing/user-data/02 user-stat-calculation.ipynb` - produces user-level statistics that are saved to SQLite DB at `data/users/users.sqlite.db`.
    3. `src/data-collection-processing/user-data/03. descriptive_user_stats.ipynb` - updates SQLite DB at `data/users/users.sqlite.db` with additional calculated statistics and produces overall descriptive statistics for the report.
    4. `src/data-collection-processing/user-data/04. adjacency-matrices.ipynb` - creates adjacency matrices used for downstream analysis tasks.
 3. To reproduce the collection of additional metadata required for user popularity regressions, run `python src/data-collection-processing/user-data/05. runner-post-metadata.py` with root directory as the working directory. Notebook `src/data-collection-processing/user-data/06. user-stat-calculation-cutoff.ipynb` should be run afterwards to create the `users_cutoff` table in the SQLite database.

As an alternative, we provide the following downloads for convenience:
 - Raw interaction data produced by step #2 above (to be stored in `data/users/raw/`) (all associated post-processing notebooks still need to be run): https://aurimasazure.blob.core.windows.net/css/raw-user-files.tar.gz (33GB)
 - Raw metadata data produced by step #3 above (to be stored in `data/users/recent`) (associated notebook needs to be run): https://aurimasazure.blob.core.windows.net/css/recent-user-files.tar.gz (114KB)
 - Fully up-to-date SQlite DB and adjacency matrices that allows skipping all data pre-processing steps and focusing on reproducing/extending user analysis (to be stored in `data/users/`): https://aurimasazure.blob.core.windows.net/css/users.tar.gz (133MB)


# Reproducing the analysis

## Text analysis

[TBD]

## User analysis
 - To reproduce the spectral clustering analysis based on user interactions, run `src/user-networks/01.clusters - direct.ipynb`  (direct interactions) and `src/user-networks/02.clusters - indirect.ipynb` (indirect interactions), respectively.
 - To reproduce the connectedness analysis based on pagerank, run `src/user-networks/03.connectedness - direct.ipynb` and `src/user-networks/04.connectedness - indirect.ipynb`, respectively.
 - To reproduce the chart on relationships between topics and users, run `src/user-networks/05.topic_user_relationships.ipynb`
 - To reproduce the user popularity analysis, run `src/user-popularity/user_influence_regressions.ipynb`

If you are using the the SQLite DB we provide, the order of notebooks are run does not matter. If you are re-creating analysis from scratch, note that there are dependencies in how the notebooks should be run (please follow the order above and ensure that you have also replicated the topic analysis / have the necessary files included in the repository). 

## User participation in other subreddits

[TBD]

# Authors

Albert Lu, Aurimas Racas, Lawton Walker
