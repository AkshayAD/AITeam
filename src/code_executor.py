import contextlib
import io
import re
from typing import Dict, Tuple, Any

import polars as pl
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def _sanitize_var_name(filename: str) -> str:
    """Convert a filename to a valid Python variable name."""
    name = filename.rsplit(".", 1)[0]
    name = re.sub(r"\W|^(?=\d)", "_", name)
    return f"df_{name}"


def execute_snippet(code: str, dataframes: Dict[str, pl.DataFrame]) -> Tuple[str, Any]:
    """Execute a Python code snippet and capture stdout and a Plotly figure.

    Parameters
    ----------
    code : str
        The Python code to execute.
    dataframes : dict
        Mapping of filename to Polars DataFrame. These will be available as
        variables in the execution context. The first dataframe will also be
        accessible as ``df``.

    Returns
    -------
    tuple
        A tuple of the captured stdout string and a Plotly figure object if a
        variable named ``fig`` is created by the code.
    """
    # Prepare execution namespace with common libraries
    local_ns = {
        "pl": pl,
        "pd": pd,
        "px": px,
        "go": go,
    }

    first_df = None
    for name, df in dataframes.items():
        var_name = _sanitize_var_name(name)
        local_ns[var_name] = df
        if first_df is None:
            first_df = df

    if first_df is not None:
        local_ns["df"] = first_df

    stdout = io.StringIO()
    try:
        with contextlib.redirect_stdout(stdout):
            exec(code, {}, local_ns)
    except Exception as e:
        stdout.write(f"\nError during execution: {e}\n")

    figure = local_ns.get("fig")
    return stdout.getvalue(), figure
