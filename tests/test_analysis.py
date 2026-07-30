"""Tests for named-query parsing and automated SQL exports."""

import json
import sqlite3

import pandas as pd
import pytest

from aquatic_wildlife.analysis import (
    parse_named_queries,
    run_sql_analyses,
)


def test_parse_named_queries(tmp_path):
    sql_path = tmp_path / "queries.sql"
    sql_path.write_text(
        """
-- name: first_query
SELECT 1 AS value;

-- name: second_query
SELECT 2 AS value;
""".strip(),
        encoding="utf-8",
    )

    queries = parse_named_queries(sql_path)

    assert list(queries) == ["first_query", "second_query"]
    assert queries["first_query"] == "SELECT 1 AS value"


def test_parser_rejects_duplicate_names(tmp_path):
    sql_path = tmp_path / "queries.sql"
    sql_path.write_text(
        """
-- name: duplicate
SELECT 1;
-- name: duplicate
SELECT 2;
""".strip(),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="Duplicate query name"):
        parse_named_queries(sql_path)


def test_run_sql_analyses_exports_results_and_manifest(tmp_path):
    database_path = tmp_path / "test.db"
    sql_path = tmp_path / "queries.sql"
    output_dir = tmp_path / "exports"

    with sqlite3.connect(database_path) as connection:
        connection.execute(
            "CREATE TABLE values_table (category TEXT, amount INTEGER)"
        )
        connection.executemany(
            "INSERT INTO values_table VALUES (?, ?)",
            [("A", 1), ("A", 2), ("B", 3)],
        )

    sql_path.write_text(
        """
-- name: category_summary
SELECT category, SUM(amount) AS total
FROM values_table
GROUP BY category
ORDER BY category;

-- name: overall_summary
SELECT COUNT(*) AS row_count, SUM(amount) AS total
FROM values_table;
""".strip(),
        encoding="utf-8",
    )

    manifest = run_sql_analyses(
        database_path=database_path,
        sql_path=sql_path,
        output_dir=output_dir,
    )

    category = pd.read_csv(output_dir / "category_summary.csv")
    summary = json.loads(
        (output_dir / "analysis_summary.json").read_text()
    )

    assert len(manifest) == 2
    assert set(manifest["status"]) == {"succeeded"}
    assert category["total"].tolist() == [3, 3]
    assert summary["query_count"] == 2
    assert (output_dir / "analysis_manifest.csv").exists()
