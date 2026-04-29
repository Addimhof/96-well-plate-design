import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans, DBSCAN
from collections import defaultdict
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

def compute_features(values, features):
    """
    Desc: Called as a micro-function of compute_features(), returning a list of values modified by a math function based on a
    feature string (used in the style of an enum).

    Pre: Needs a list of values to edit as well as a feature string e.g. "total", "peak", "ending"

    Post: Returns a copied list of modified values.
    """
    out = []
    if "total" in features:
        out.append(sum(values))
    if "peak" in features:
        out.append(max(values))
    if "ending" in features:
        out.append(values[-1])
    return out

def build_feature_matrix(well_data, signal_key, features,
                         selected_wells=None,
                         include_promoter=False,
                         include_ahl=False):
    """
    Desc: Builds a matrix of vector features from either all wells or a subset of wells based on the params (see below) specified. 

    Pre: For a list of all of the parameters passed to the function, look below in its own section for a description of each.

    Post: Returns a numpy array mapping well labels to calculated vector features of each well.

    Parameters (Included since there's quite a few):
        -well_data: Pass all the wells into this function.
        
        -signal_key: Decides whether RFU or OD is used during compute_features(), relative to time signature.

        -features: A string signal key used to call compute_features(). Default NoneType.

        -include_promoter: tk Boolval to include promoter mutants as a clustering factor. Default False.

        -include_ahl: tk Boolval to include AHL levels as a clustering factor. Default False.
    """
    # X: Feature vector list
    # labels: Well id list
    X, labels = [], []
    # If the user specifies a value for selected_wells, use the subset, otherwise just use all wells.
    wells_to_use = selected_wells if selected_wells else well_data.keys()

    # --- Encode categorical values ---
    # Extract all unique promoter categories for ordering. Create a dict to map promoters to wells.
    promoters = sorted({well_data[w]["promoter"] for w in wells_to_use})
    promoter_map = {p: i for i, p in enumerate(promoters)}

    # Extract all unique AHL levels for ordering. Create a dict to map AHL to wells.
    ahl_values = sorted({well_data[w]["ahl"] for w in wells_to_use})
    ahl_map = {a: i for i, a in enumerate(ahl_values)}

    for well in wells_to_use:
        # vec stores each applicable vector feature, based on signal_key (if it exists), the include promoter and ahl bools,
        # and if vec stores any present data.
        vec = []

        # Signal features
        if signal_key:
            #Include all of the important signal features in vec if there's a key.
            vec.extend(compute_features(well_data[well][signal_key.lower()], features))

        # Promoter encoding
        if include_promoter:
            # Add categorical data as integers
            # Note that defaulting to 0 can create bias
            vec.append(promoter_map.get(well_data[well]["promoter"], 0))

        # AHL encoding
        if include_ahl:
            # Add categorical data as integers
            # Note that defaulting to 0 can create bias
            vec.append(ahl_map.get(well_data[well]["ahl"], 0))

        if vec:
            # Append X with the currently grabbed vector data
            X.append(vec)
            # Assign a label to the well for which the vec applies
            labels.append(well)
    # Return everything as a numpy array
    return np.array(X), labels

def cluster_signal(X, clustering_mode="kmeans", n_clusters=4, dbscan_eps=0.5):
    """
    Desc: Uses one of two machine learning algorithms (kmeans or DBSCAN) to create an array of cluster references for datapoints (cluster_ids),
    which is returned when called.

    Pre: Pass a vector to standardize scaling (X), choose a clustering mode (either "kmeans" else DBSCAN), a number of clusters for kmeans
    (n_clusters; default 4) and a DBSCAN epsilon (dbscan_eps; default 0.5). For DBSCAN epsilon see plot_clusters_gui() for what that is.

    Post: Returns a numpy array of every data cluster analyzed.
    """
    # if else selects a learning model. By default, it's DBSCAN, otherwise KMeans
    if clustering_mode.lower() == "kmeans":
        # KMeans procedure: Partition dataset into n clusters. Assign each sample to nearest centroid.
        model = KMeans(n_clusters=n_clusters, random_state=42)
        # Because means are skewed by outliers everything needs to be normalized by StandardScalar
        cluster_ids = model.fit_predict(StandardScaler().fit_transform(X))
    else:
        # DBSCAN clusters based on density, allowing for automatic assigning of a number of samples, minimum 2.
        # Individual points are specified as noise (-1)
        cluster_ids = DBSCAN(eps=dbscan_eps, min_samples=2).fit_predict(
            # First we also need to scale this too, for the same reason as KMeans.
            StandardScaler().fit_transform(X)
        )
        # convert outliers (-1) to unique clusters
        # Every cluster must be treated as meaningful data
        new_clusters = []
        # The largest cluster is declared a maximum for some checks.
        max_c = max(cluster_ids) if cluster_ids.size > 0 else -1
        for c in cluster_ids:
            if c == -1:
                # If there is noise, treat maximum cluster as larger, then add it to the new_clusters
                max_c += 1
                new_clusters.append(max_c)
            else:
                # If not noise, just append the cluster to the list of clusters.
                new_clusters.append(c)
        # Update the cluster_ids with the new data, then return it.
        cluster_ids = np.array(new_clusters)
    return cluster_ids

def build_cluster_map(labels, cluster_ids):
    """
    Desc: Builds a hashmap (dict) via iterator out of well labels and cluster_ids so that clusters can be referenced by well.

    Pre: Needs lists of labels and cluster_ids (returned by cluster_signal()).

    Post: Returns the cluster_map dictionary
    """
    cluster_map = defaultdict(list)
    for well, cid in zip(labels, cluster_ids):
        cluster_map[cid].append(well)
    return cluster_map
