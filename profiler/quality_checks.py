from __future__ import annotations

import warnings
from typing import Any

import pandas as pd


def _missing_percent(series: pd.Series, row_count: int) -> float:
	if row_count == 0:
		return 0.0
	return round((int(series.isna().sum()) / row_count) * 100, 2)


def build_quality_checks(dataframe: pd.DataFrame) -> dict[str, Any]:
	row_count = int(len(dataframe))
	duplicate_row_count = int(dataframe.duplicated(keep="first").sum())
	duplicate_row_percent = round((duplicate_row_count / row_count) * 100, 2) if row_count else 0.0

	findings: list[dict[str, Any]] = []

	if duplicate_row_count > 0:
		findings.append(
			{
				"check_name": "Duplicate Rows",
				"severity": "warning",
				"column_name": None,
				"message": f"Detected {duplicate_row_count} duplicate rows.",
			}
		)

	for column_name in dataframe.columns.tolist():
		series = dataframe[column_name]
		non_null_series = series.dropna()
		non_null_count = int(non_null_series.shape[0])
		distinct_non_null_count = int(non_null_series.nunique())
		column_name_lower = str(column_name).lower()

		missing_percent = _missing_percent(series, row_count)
		if missing_percent >= 50.0:
			findings.append(
				{
					"check_name": "Blank-Heavy Column",
					"severity": "warning",
					"column_name": column_name,
					"message": f"Column has {missing_percent}% missing values.",
				}
			)

		if row_count > 0 and non_null_count > 0 and distinct_non_null_count == 1:
			findings.append(
				{
					"check_name": "Constant Column",
					"severity": "info",
					"column_name": column_name,
					"message": "Column has one distinct non-null value.",
				}
			)

		if "id" in column_name_lower and non_null_count > 0 and distinct_non_null_count == non_null_count:
			findings.append(
				{
					"check_name": "Possible ID Column",
					"severity": "info",
					"column_name": column_name,
					"message": "Column name suggests an identifier and non-null values are unique.",
				}
			)

		is_text_column = pd.api.types.is_object_dtype(series) or pd.api.types.is_string_dtype(series)
		if is_text_column and non_null_count >= 10:
			distinct_ratio = distinct_non_null_count / non_null_count
			if distinct_ratio >= 0.8:
				findings.append(
					{
						"check_name": "High-Variety Text Column",
						"severity": "info",
						"column_name": column_name,
						"message": (
							f"Column has many distinct text values: {distinct_non_null_count} distinct values "
							f"across {non_null_count} non-null rows. This may be expected for names, "
							"descriptions, or free-text fields."
						),
					}
				)

		is_date_name_hint = any(token in column_name_lower for token in ["date", "time", "dt"])
		is_parseable_date = False
		is_datetime_column = pd.api.types.is_datetime64_any_dtype(series)
		if non_null_count > 0 and is_datetime_column:
			is_parseable_date = True
		elif non_null_count > 0 and is_text_column:
			with warnings.catch_warnings():
				warnings.simplefilter("ignore", UserWarning)
				parsed_values = pd.to_datetime(non_null_series, errors="coerce")
			parsed_non_null_count = int(parsed_values.notna().sum())
			parseable_ratio = parsed_non_null_count / non_null_count
			is_parseable_date = parseable_ratio >= 0.8

		if non_null_count > 0 and (is_date_name_hint or is_parseable_date):
			if is_date_name_hint and is_parseable_date:
				message = "Column name suggests date/time values, and most non-null values parse as dates."
			elif is_date_name_hint:
				message = "Column name suggests this column may contain date/time values."
			else:
				message = "Most non-null values parse as dates."

			findings.append(
				{
					"check_name": "Possible Date Column",
					"severity": "info",
					"column_name": column_name,
					"message": message,
				}
			)

		if is_text_column and non_null_count >= 5:
			evaluated_series = non_null_series.astype(str).str.strip()
			evaluated_series = evaluated_series[evaluated_series != ""]
			evaluated_count = int(evaluated_series.shape[0])

			if evaluated_count >= 5:
				numeric_like_series = pd.to_numeric(evaluated_series, errors="coerce")
				numeric_like_count = int(numeric_like_series.notna().sum())
				text_like_count = evaluated_count - numeric_like_count

				numeric_like_ratio = numeric_like_count / evaluated_count
				text_like_ratio = text_like_count / evaluated_count

				if (
					numeric_like_count > 0
					and text_like_count > 0
					and numeric_like_ratio >= 0.2
					and text_like_ratio >= 0.2
				):
					findings.append(
						{
							"check_name": "Suspicious Mixed-Type Column",
							"severity": "warning",
							"column_name": column_name,
							"message": (
								"Column mixes numeric-like and text-like values: "
								f"{numeric_like_count} numeric-like and {text_like_count} text-like values "
								f"across {evaluated_count} evaluated rows."
							),
						}
					)

	return {
		"row_count": row_count,
		"duplicate_row_count": duplicate_row_count,
		"duplicate_row_percent": duplicate_row_percent,
		"findings": findings,
	}
