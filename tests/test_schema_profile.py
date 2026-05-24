import pandas as pd

from profiler.schema_profile import build_schema_profile


def test_build_schema_profile_returns_expected_summary():
	dataframe = pd.DataFrame(
		{
			"name": ["Alice", "Bob", "Alice", None],
			"age": [30, 25, 30, 25],
		}
	)

	profile = build_schema_profile(dataframe)

	assert profile["row_count"] == 4
	assert profile["column_count"] == 2
	assert [column["column_name"] for column in profile["columns"]] == ["name", "age"]

	name_column = profile["columns"][0]
	age_column = profile["columns"][1]

	assert name_column["missing_count"] == 1
	assert name_column["missing_percent"] == 25.0
	assert name_column["distinct_count"] == 2
	assert name_column["sample_values"] == ["Alice", "Bob"]

	assert age_column["missing_count"] == 0
	assert age_column["missing_percent"] == 0.0
	assert age_column["distinct_count"] == 2
	assert age_column["sample_values"] == [30, 25]


def test_build_schema_profile_handles_empty_dataframe():
	dataframe = pd.DataFrame(columns=["name", "age"])

	profile = build_schema_profile(dataframe)

	assert profile["row_count"] == 0
	assert profile["column_count"] == 2
	assert [column["column_name"] for column in profile["columns"]] == ["name", "age"]
	for column in profile["columns"]:
		assert column["missing_count"] == 0
		assert column["missing_percent"] == 0.0
		assert column["distinct_count"] == 0
		assert column["sample_values"] == []


def test_build_schema_profile_handles_all_null_column():
	dataframe = pd.DataFrame({"all_null": [None, None, None]})

	profile = build_schema_profile(dataframe)
	all_null_column = profile["columns"][0]

	assert all_null_column["column_name"] == "all_null"
	assert all_null_column["missing_count"] == 3
	assert all_null_column["missing_percent"] == 100.0
	assert all_null_column["distinct_count"] == 0
	assert all_null_column["sample_values"] == []


def test_build_schema_profile_missing_percent_calculation():
	dataframe = pd.DataFrame({"status": ["ok", None, None, "ok"]})

	profile = build_schema_profile(dataframe)
	status_column = profile["columns"][0]

	assert status_column["missing_count"] == 2
	assert status_column["missing_percent"] == 50.0


def test_build_schema_profile_sample_values_limited_and_deterministic():
	dataframe = pd.DataFrame(
		{
			"items": [
				"A",
				"B",
				"A",
				None,
				"C",
				"D",
				"E",
				"F",
				"G",
			]
		}
	)

	profile = build_schema_profile(dataframe)
	items_column = profile["columns"][0]

	assert items_column["sample_values"] == ["A", "B", "C", "D", "E"]
