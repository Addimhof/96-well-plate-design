import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans, DBSCAN
from collections import defaultdict
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

def compute_features(values, features):
    out = []
    if "total" in features:
        out.append(sum(values))
    if "peak" in features:
        out.append(max(values))
    if "ending" in features:
        out.append(values[-1])
    return out

def build_feature_matrix(well_data, signal_key, features, selected_wells=None):
    X, labels = [], []
    wells_to_use = selected_wells if selected_wells else well_data.keys()
    for well in wells_to_use:
        vec = compute_features(well_data[well][signal_key.lower()], features)
        if vec:
            X.append(vec)
            labels.append(well)
    return np.array(X), labels

def cluster_signal(X, clustering_mode="kmeans", n_clusters=4, dbscan_eps=0.5):
    if clustering_mode.lower() == "kmeans":
        model = KMeans(n_clusters=n_clusters, random_state=42)
        cluster_ids = model.fit_predict(StandardScaler().fit_transform(X))
    else:
        cluster_ids = DBSCAN(eps=dbscan_eps, min_samples=2).fit_predict(
            StandardScaler().fit_transform(X)
        )
        # convert outliers (-1) to unique clusters
        new_clusters = []
        max_c = max(cluster_ids) if cluster_ids.size > 0 else -1
        for c in cluster_ids:
            if c == -1:
                max_c += 1
                new_clusters.append(max_c)
            else:
                new_clusters.append(c)
        cluster_ids = np.array(new_clusters)
    return cluster_ids

def build_cluster_map(labels, cluster_ids):
    cluster_map = defaultdict(list)
    for well, cid in zip(labels, cluster_ids):
        cluster_map[cid].append(well)
    return cluster_map
