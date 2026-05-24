from __future__ import annotations

from typing import Any

import pandas as pd


def _sample_values(series: pd.Series, limit: int = 5) -> list[Any]:
	if limit <= 0:
		return []

	samples: list[Any] = []
	for value in series.tolist():
		if pd.isna(value):
			continue
		if value not in samples:
			samples.append(value)
		if len(samples) >= limit:
			break
	return samples


def build_schema_profile(dataframe: pd.DataFrame) -> dict[str, Any]:
	row_count = int(len(dataframe))
	column_count = int(len(dataframe.columns))

	columns: list[dict[str, Any]] = []
	for column_name in dataframe.columns.tolist():
		series = dataframe[column_name]
		missing_count = int(series.isna().sum())
		missing_percent = round((missing_count / row_count) * 100, 2) if row_count else 0.0

		columns.append(
			{
				"column_name": column_name,
				"inferred_dtype": str(series.dtype),
				"missing_count": missing_count,
				"missing_percent": missing_percent,
				"distinct_count": int(series.nunique(dropna=True)),
				"sample_values": _sample_values(series),
			}
		)

	return {
		"row_count": row_count,
		"column_count": column_count,
		"columns": columns,
	}
