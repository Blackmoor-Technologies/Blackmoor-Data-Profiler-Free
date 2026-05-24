from __future__ import annotations

from typing import Any


SUGGESTED_DESCRIPTION_PLACEHOLDER = "TODO: Describe the business meaning of this field."


def build_data_dictionary(profile: dict[str, Any]) -> list[dict[str, Any]]:
	rows: list[dict[str, Any]] = []
	for column in profile.get("columns", []):
		sample_values = column.get("sample_values")
		if isinstance(sample_values, list):
			safe_sample_values = sample_values
		else:
			safe_sample_values = []

		rows.append(
			{
				"column_name": column.get("column_name"),
				"inferred_dtype": column.get("inferred_dtype"),
				"suggested_description": SUGGESTED_DESCRIPTION_PLACEHOLDER,
				"missing_percent": column.get("missing_percent"),
				"distinct_count": column.get("distinct_count"),
				"sample_values": safe_sample_values,
			}
		)

	return rows