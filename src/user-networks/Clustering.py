import numpy as np
from sklearn.cluster import MiniBatchKMeans
from sklearn import metrics
import pandas as pd
import itertools as itt
import altair as alt
from collections import Counter
import polars as pl


def spectral_clustering(A, max_clusters=10):

    #calculate the Graph Laplacian manually
    D = np.diag(np.sum(A, axis=1))
    L = np.subtract(D, A)
    L = L.astype(int)

    print("Computing eigenvalues..")
    vals, vecs = np.linalg.eigh(L)    #retrieve eigenvalues
    selected_vecs = vecs[:, range(max_clusters + 1)] #get the vectors of n-smallest eigenvalues
    eigvalues = list(zip(vals, itt.count()))

    print("Running K-means..")
    #Try Kmeans and report scores
    results = []
    sizes = []
    for k in range(2, max_clusters + 1):
        vecs = selected_vecs[:,:k]
        clusters = MiniBatchKMeans(n_clusters=k, max_iter=1000, random_state=42).fit(vecs)
        cluster_sizes = sorted(Counter(clusters.labels_).values(), reverse=True)
        sizes.append((k, list(zip(itt.count(), cluster_sizes))))
        s = metrics.silhouette_score(vecs, clusters.labels_)    
        results.append((k, s))

    return selected_vecs, results, sizes, eigvalues

def plot_cluster_diagnostics(results, sizes, eigvalues):

    #plot eigenvalues to understand how they evolve
    c1 = alt.Chart(pd.DataFrame(eigvalues, columns=['eigenvalue', 'index']).head(30)).mark_line().encode(
        x='index',
        y='eigenvalue'
    ).properties(title="Eigenvalue magnitude", width=300)


    #plot silhouette scores
    clustering_performance = pd.DataFrame(results, columns=["No_clusters", "Silhouette score"])
    c2 = alt.Chart(clustering_performance).mark_point().encode(
        x="No_clusters",
        y='Silhouette score',
    ).properties(title="Silhouette scores", width=300).interactive()


    cl_df = pd.DataFrame(sizes, columns=['no_clusters', 'temp']).explode('temp')
    cl_df['cluster'] = cl_df['temp'].apply(lambda x: x[0])
    cl_df['cluster_size'] = cl_df['temp'].apply(lambda x: x[1])

    c3 = alt.Chart(cl_df).mark_bar().encode(
        x='no_clusters:O',
        y='cluster_size',
        color=alt.Color('cluster:O', scale=alt.Scale(scheme='dark2'))
    ).properties(title="Cluster sizes", width=300)

    return (c1 | c2 | c3)

def get_basic_stats(df): 
    stats = df.lazy().groupby("cluster").agg([
            pl.col("no_posts").count().alias("Total number of users"),              
            pl.col("no_posts").median().alias("Median posts per user"),             
            pl.col("no_comments").median().alias("Median comments per user"),    
            (pl.col("activity_window")).median().alias("Median activity window (days)"),                        
            (pl.col("avg_post_karma")).median().alias("Median average post karma"),
            (pl.col("avg_comment_karma")).median().alias("Median average comment karma"),
        ]).collect().filter(pl.col("Total number of users") > 100).transpose(include_header=True, header_name="Statistic")
    return stats