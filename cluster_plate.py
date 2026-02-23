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

def build_feature_matrix(well_data, signal_key, features,
                         selected_wells=None,
                         include_promoter=False,
                         include_ahl=False):

    X, labels = [], []
    wells_to_use = selected_wells if selected_wells else well_data.keys()

    # --- Encode categorical values ---
    promoters = sorted({well_data[w]["promoter"] for w in wells_to_use})
    promoter_map = {p: i for i, p in enumerate(promoters)}

    ahl_values = sorted({well_data[w]["ahl"] for w in wells_to_use})
    ahl_map = {a: i for i, a in enumerate(ahl_values)}

    for well in wells_to_use:
        vec = []

        # Signal features
        if signal_key:
            vec.extend(compute_features(well_data[well][signal_key.lower()], features))

        # Promoter encoding
        if include_promoter:
            vec.append(promoter_map.get(well_data[well]["promoter"], 0))

        # AHL encoding
        if include_ahl:
            vec.append(ahl_map.get(well_data[well]["ahl"], 0))

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
