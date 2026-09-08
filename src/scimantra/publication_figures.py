"""Publication-oriented figure helpers with transparent data provenance."""
from __future__ import annotations

import io
import matplotlib.pyplot as plt
import pandas as pd


def figure_types() -> list[str]:
    return ["Scatter", "Boxplot", "Violin", "Bar + individual observations", "Line"]


def make_figure(df: pd.DataFrame, kind: str, x: str, y: str):
    fig, ax = plt.subplots(figsize=(8, 5), constrained_layout=True)
    if kind == "Scatter":
        ax.scatter(df[x], pd.to_numeric(df[y], errors="coerce"), alpha=0.75)
        ax.set_xlabel(x); ax.set_ylabel(y)
    elif kind in {"Boxplot", "Violin", "Bar + individual observations"}:
        groups = [g for _, g in df.groupby(x, dropna=True)]
        labels = [str(g[x].iloc[0]) for g in groups]
        values = [pd.to_numeric(g[y], errors="coerce").dropna().values for g in groups]
        if kind == "Boxplot":
            ax.boxplot(values, labels=labels, showmeans=True)
        elif kind == "Violin":
            ax.violinplot(values, showmeans=True, showmedians=True)
            ax.set_xticks(range(1, len(labels)+1), labels)
        else:
            means = [v.mean() if len(v) else float("nan") for v in values]
            ax.bar(range(len(labels)), means)
            for i, vals in enumerate(values):
                ax.scatter([i] * len(vals), vals, alpha=0.65)
            ax.set_xticks(range(len(labels)), labels)
        ax.set_xlabel(x); ax.set_ylabel(y)
    elif kind == "Line":
        work = df[[x, y]].copy().dropna().sort_values(x)
        ax.plot(work[x], pd.to_numeric(work[y], errors="coerce"), marker="o")
        ax.set_xlabel(x); ax.set_ylabel(y)
    ax.set_title(f"{y} by {x}")
    return fig


def figure_png(fig) -> bytes:
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=300, bbox_inches="tight")
    plt.close(fig)
    return buf.getvalue()
