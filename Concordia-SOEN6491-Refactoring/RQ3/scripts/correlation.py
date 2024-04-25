from util import *

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd


path_mtrs = PATH_SCRIPT / "out" / "metrics"

path_out = PATH_SCRIPT / "out" / 'correlation'
path_out.mkdir(parents=True, exist_ok=True)


def correlation(df:pd.DataFrame, mtr_save_path, fig_save_path):
    # Calculate Spearman's rank correlation matrix
        correlation_matrix = df.corr(method='spearman')
        correlation_matrix.to_csv(mtr_save_path)

        #  visualize the correlation matrix using a heatmap
        plt.figure(figsize=(10, 8))
        sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', fmt=".2f", xticklabels=df.columns, yticklabels=df.columns)
        plt.title("Spearman's Rank Correlation Matrix")
        plt.xlabel("Variables")
        plt.ylabel("Variables")
        plt.tight_layout()
        plt.savefig(fig_save_path)


def main():
    """
    compute the Spearman’s rank correlation between all possible pairs of columns in the normalized dataset, 
    to determine whether there are pairs of strongly correlated metrics
    """
    path_input = path_mtrs / 'normalized'

    projects = path_input.glob('*.csv')
    for pro in projects:
        df = pd.read_csv(pro)
        metrics_df = df[METRIC_COLUMNS]

        correlation(metrics_df, path_out / f'{pro.stem}.csv', path_out / f"{pro.stem}.png")


main()
