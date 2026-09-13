"""In-memory DuckDB analytical layer."""

from __future__ import annotations

from pathlib import Path

import duckdb
import pandas as pd


def initialize_database(orders: pd.DataFrame) -> duckdb.DuckDBPyConnection:
    """Register cleaned orders as the read-only analytical source view."""
    connection = duckdb.connect(database=":memory:")
    connection.register("orders_frame", orders)
    connection.execute("CREATE VIEW orders AS SELECT * FROM orders_frame")
    return connection


def run_sql_file(connection: duckdb.DuckDBPyConnection, path: str | Path) -> pd.DataFrame:
    """Execute a version-controlled SQL mart and return a DataFrame."""
    return connection.execute(Path(path).read_text(encoding="utf-8")).fetchdf()
