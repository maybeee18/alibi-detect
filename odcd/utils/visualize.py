import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from typing import Dict


def plot_instance_outlier(od_preds: Dict,
                          target: np.ndarray,
                          labels: np.ndarray,
                          threshold: float) -> None:
    """
    Scatter plot of a batch of outlier scores compared to the outlier threshold.

    Parameters
    ----------
    scores
        Outlier scores.
    target
        Ground truth.
    labels
        List with names of classification labels.
    threshold
        Threshold used to classify outliers.
    """
    scores = od_preds['data']['instance_score']
    df = pd.DataFrame(dict(idx=np.arange(len(scores)), score=scores, label=target))
    groups = df.groupby('label')
    fig, ax = plt.subplots()
    for name, group in groups:
        ax.plot(group.idx, group.score, marker='o', linestyle='', ms=6, label=labels[name])
    plt.plot(np.arange(len(scores)), np.ones(len(scores)) * threshold, color='g', label='Threshold')
    plt.xlabel('Number of Instances')
    plt.ylabel('Instance Level Outlier Score')
    ax.legend()
    plt.show()


def plot_feature_outlier_image(od_preds: Dict,
                               X: np.ndarray,
                               X_recon: np.ndarray = None,
                               instance_ids: list = None,
                               max_instances: int = 5,
                               outliers_only: bool = False,
                               n_channels: int = 3,
                               figsize: tuple = (20, 20)) -> None:
    """
    Plot feature (pixel) wise outlier scores for images.

    Parameters
    ----------
    od_preds
        Output of an outlier detector's prediction.
    X
        Batch of instances to apply outlier detection to.
    X_recon
        Reconstructed instances of X.
    instance_ids
        List with indices of instances to display.
    max_instances
        Maximum number of instances to display.
    outliers_only
        Whether to only show outliers or not.
    n_channels
        Number of channels of the images.
    figsize
        Tuple for the figure size.
    """
    scores = od_preds['data']['feature_score']
    if outliers_only and instance_ids is None:
        instance_ids = list(np.where(od_preds['data']['is_outlier'])[0])
    elif instance_ids is None:
        instance_ids = list(range(len(od_preds['data']['is_outlier'])))
    n_instances = min(max_instances, len(instance_ids))
    instance_ids = instance_ids[:n_instances]
    n_cols = 2

    if n_channels == 3:
        n_cols += 2

    if X_recon is not None:
        n_cols += 1

    fig, axes = plt.subplots(nrows=n_instances, ncols=n_cols, figsize=figsize)

    n_subplot = 1
    for i in range(n_instances):

        idx = instance_ids[i]

        X_outlier = X[idx]
        plt.subplot(n_instances, n_cols, n_subplot)
        plt.axis('off')
        if i == 0:
            plt.title('Original')
        plt.imshow(X_outlier)
        n_subplot += 1

        if X_recon is not None:
            plt.subplot(n_instances, n_cols, n_subplot)
            plt.axis('off')
            if i == 0:
                plt.title('Reconstruction')
            plt.imshow(X_recon[idx])
            n_subplot += 1

        plt.subplot(n_instances, n_cols, n_subplot)
        plt.axis('off')
        if i == 0:
            plt.title('Outlier Score Channel 0')
        plt.imshow(scores[idx][:, :, 0])
        n_subplot += 1

        if n_channels == 3:
            plt.subplot(n_instances, n_cols, n_subplot)
            plt.axis('off')
            if i == 0:
                plt.title('Outlier Score Channel 1')
            plt.imshow(scores[idx][:, :, 1])
            n_subplot += 1

            plt.subplot(n_instances, n_cols, n_subplot)
            plt.axis('off')
            if i == 0:
                plt.title('Outlier Score Channel 2')
            plt.imshow(scores[idx][:, :, 2])
            n_subplot += 1

    plt.show()


def plot_feature_outlier_tabular(od_preds: Dict,
                                 X: np.ndarray,
                                 X_recon: np.ndarray = None,
                                 threshold: float = None,
                                 instance_ids: list = None,
                                 max_instances: int = 5,
                                 top_n: int = int(1e12),
                                 outliers_only: bool = False,
                                 feature_names: list = None,
                                 width: float = .2,
                                 figsize: tuple = (20, 10)) -> None:
    """
    Plot feature wise outlier scores for tabular data.

    Parameters
    ----------
    od_preds
        Output of an outlier detector's prediction.
    X
        Batch of instances to apply outlier detection to.
    X_recon
        Reconstructed instances of X.
    threshold
        Threshold used for outlier score to determine outliers.
    instance_ids
        List with indices of instances to display.
    max_instances
        Maximum number of instances to display.
    top_n
        Maixmum number of features to display, ordered by outlier score.
    outliers_only
        Whether to only show outliers or not.
    feature_names
        List with feature names.
    width
        Column width for bar charts.
    figsize
        Tuple for the figure size.
    """
    if outliers_only and instance_ids is None:
        instance_ids = list(np.where(od_preds['data']['is_outlier'])[0])
    elif instance_ids is None:
        instance_ids = list(range(len(od_preds['data']['is_outlier'])))
    n_instances = min(max_instances, len(instance_ids))
    instance_ids = instance_ids[:n_instances]
    n_features = X.shape[1]
    n_cols = 2

    labels_values = ['Original']
    if X_recon is not None:
        labels_values += ['Reconstructed']
    labels_scores = ['Outlier Score']
    if threshold is not None:
        labels_scores = ['Threshold'] + labels_scores

    fig, axes = plt.subplots(nrows=n_instances, ncols=n_cols, figsize=figsize)

    n_subplot = 1
    for i in range(n_instances):

        idx = instance_ids[i]

        fscore = od_preds['data']['feature_score'][idx]
        if top_n >= n_features:
            keep_cols = np.arange(n_features)
        else:
            keep_cols = np.argsort(fscore)[::-1][:top_n]
        fscore = fscore[keep_cols]
        X_idx = X[idx][keep_cols]
        ticks = np.arange(len(keep_cols))

        plt.subplot(n_instances, n_cols, n_subplot)
        if X_recon is not None:
            X_recon_idx = X_recon[idx][keep_cols]
            plt.bar(ticks - width, X_idx, width=width, color='b', align='center')
            plt.bar(ticks, X_recon_idx, width=width, color='g', align='center')
        else:
            plt.bar(ticks, X_idx, width=width, color='b', align='center')
        if feature_names is not None:
            plt.xticks(ticks=ticks, labels=feature_names, rotation=45)
        plt.title('Feature Values')
        plt.xlabel('Features')
        plt.ylabel('Feature Values')
        plt.legend(labels_values)
        n_subplot += 1

        plt.subplot(n_instances, n_cols, n_subplot)
        plt.bar(ticks, fscore)
        if threshold is not None:
            plt.plot(np.ones(len(ticks)) * threshold, 'r')
        if feature_names is not None:
            plt.xticks(ticks=ticks, labels=feature_names, rotation=45)
        plt.title('Feature Level Outlier Score')
        plt.xlabel('Features')
        plt.ylabel('Outlier Score')
        plt.legend(labels_scores)
        n_subplot += 1

    plt.tight_layout()
    plt.show()


def plot_feature_outlier_ts():
    pass
