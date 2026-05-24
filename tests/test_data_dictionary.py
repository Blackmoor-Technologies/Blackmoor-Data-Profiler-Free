from profiler.data_dictionary import SUGGESTED_DESCRIPTION_PLACEHOLDER, build_data_dictionary


def test_build_data_dictionary_builds_one_row_per_column():
	profile = {
		"columns": [
			{"column_name": "a", "inferred_dtype": "int64", "missing_percent": 0.0, "distinct_count": 1},
			{"column_name": "b", "inferred_dtype": "object", "missing_percent": 50.0, "distinct_count": 2},
		]
	}

	rows = build_data_dictionary(profile)

	assert len(rows) == 2


def test_build_data_dictionary_includes_core_fields_and_placeholder_description():
	profile = {
		"columns": [
			{
				"column_name": "customer_id",
				"inferred_dtype": "int64",
				"missing_percent": 0.0,
				"distinct_count": 3,
				"sample_values": [1001, 1002],
			}
		]
	}

	rows = build_data_dictionary(profile)
	row = rows[0]

	assert row["column_name"] == "customer_id"
	assert row["inferred_dtype"] == "int64"
	assert row["suggested_description"] == SUGGESTED_DESCRIPTION_PLACEHOLDER
	assert row["missing_percent"] == 0.0
	assert row["distinct_count"] == 3
	assert row["sample_values"] == [1001, 1002]


def test_build_data_dictionary_handles_missing_optional_fields_gracefully():
	profile = {
		"columns": [
			{
				"column_name": "notes",
				"inferred_dtype": "object",
			}
		]
	}

	rows = build_data_dictionary(profile)
	row = rows[0]

	assert row["column_name"] == "notes"
	assert row["inferred_dtype"] == "object"
	assert row["suggested_description"] == SUGGESTED_DESCRIPTION_PLACEHOLDER
	assert row["missing_percent"] is None
	assert row["distinct_count"] is None
	assert row["sample_values"] == []


def test_build_data_dictionary_non_list_sample_values_defaults_to_empty_list():
	profile = {
		"columns": [
			{
				"column_name": "status",
				"inferred_dtype": "object",
				"sample_values": "active",
			}
		]
	}

	rows = build_data_dictionary(profile)

	assert rows[0]["sample_values"] == []