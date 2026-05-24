import pandas as pd

from profiler.quality_checks import build_quality_checks


def test_build_quality_checks_duplicate_rows_count_and_percent():
	dataframe = pd.DataFrame(
		{
			"name": ["Alice", "Alice", "Bob"],
			"age": [30, 30, 40],
		}
	)

	checks = build_quality_checks(dataframe)

	assert checks["row_count"] == 3
	assert checks["duplicate_row_count"] == 1
	assert checks["duplicate_row_percent"] == 33.33
	duplicate_findings = [f for f in checks["findings"] if f["check_name"] == "Duplicate Rows"]
	assert len(duplicate_findings) == 1
	assert duplicate_findings[0]["column_name"] is None


def test_build_quality_checks_blank_heavy_column_finding():
	dataframe = pd.DataFrame(
		{
			"optional_note": [None, None, "note", None],
			"value": [1, 2, 3, 4],
		}
	)

	checks = build_quality_checks(dataframe)
	blank_heavy_findings = [f for f in checks["findings"] if f["check_name"] == "Blank-Heavy Column"]

	assert len(blank_heavy_findings) == 1
	assert blank_heavy_findings[0]["column_name"] == "optional_note"
	assert blank_heavy_findings[0]["severity"] == "warning"


def test_build_quality_checks_constant_column_finding():
	dataframe = pd.DataFrame(
		{
			"status": ["active", "active", "active"],
			"value": [1, 2, 3],
		}
	)

	checks = build_quality_checks(dataframe)
	constant_findings = [f for f in checks["findings"] if f["check_name"] == "Constant Column"]

	assert len(constant_findings) == 1
	assert constant_findings[0]["column_name"] == "status"
	assert constant_findings[0]["severity"] == "info"


def test_build_quality_checks_possible_id_column_finding():
	dataframe = pd.DataFrame(
		{
			"customer_id": [101, 102, 103],
			"name": ["Alice", "Bob", "Cara"],
		}
	)

	checks = build_quality_checks(dataframe)
	id_findings = [f for f in checks["findings"] if f["check_name"] == "Possible ID Column"]

	assert len(id_findings) == 1
	assert id_findings[0]["column_name"] == "customer_id"
	assert id_findings[0]["severity"] == "info"
	assert "suggests an identifier" in id_findings[0]["message"]
	assert "non-null values are unique" in id_findings[0]["message"]


def test_build_quality_checks_no_findings_for_clean_dataframe():
	dataframe = pd.DataFrame(
		{
			"name": ["Alice", "Bob", "Cara"],
			"score": [10, 20, 30],
		}
	)

	checks = build_quality_checks(dataframe)

	assert checks["duplicate_row_count"] == 0
	assert checks["duplicate_row_percent"] == 0.0
	assert checks["findings"] == []


def test_build_quality_checks_high_variety_text_column_finding():
	dataframe = pd.DataFrame(
		{
			"event_code": [
				"A1",
				"A2",
				"A3",
				"A4",
				"A5",
				"A6",
				"A7",
				"A8",
				"A9",
				"A10",
			],
		}
	)

	checks = build_quality_checks(dataframe)
	high_variety_findings = [
		f for f in checks["findings"] if f["check_name"] == "High-Variety Text Column"
	]

	assert len(high_variety_findings) == 1
	assert high_variety_findings[0]["column_name"] == "event_code"
	assert high_variety_findings[0]["severity"] == "info"
	assert "many distinct text values" in high_variety_findings[0]["message"]
	assert "This may be expected" in high_variety_findings[0]["message"]


def test_build_quality_checks_low_cardinality_text_column_not_flagged():
	dataframe = pd.DataFrame(
		{
			"status": [
				"open",
				"open",
				"closed",
				"open",
				"closed",
				"open",
				"closed",
				"open",
				"closed",
				"open",
			],
		}
	)

	checks = build_quality_checks(dataframe)
	high_variety_findings = [
		f for f in checks["findings"] if f["check_name"] == "High-Variety Text Column"
	]

	assert high_variety_findings == []


def test_build_quality_checks_possible_date_column_by_name():
	dataframe = pd.DataFrame(
		{
			"order_date": ["not-a-date", "still-not-a-date", "value"],
			"name": ["Alice", "Bob", "Cara"],
		}
	)

	checks = build_quality_checks(dataframe)
	date_findings = [f for f in checks["findings"] if f["check_name"] == "Possible Date Column"]

	assert len(date_findings) == 1
	assert date_findings[0]["column_name"] == "order_date"
	assert date_findings[0]["severity"] == "info"


def test_build_quality_checks_possible_date_column_by_parseable_values():
	dataframe = pd.DataFrame(
		{
			"event_value": ["2024-01-01", "2024-01-02", "2024-01-03", "bad", "2024-01-05"],
		}
	)

	checks = build_quality_checks(dataframe)
	date_findings = [f for f in checks["findings"] if f["check_name"] == "Possible Date Column"]

	assert len(date_findings) == 1
	assert date_findings[0]["column_name"] == "event_value"
	assert date_findings[0]["severity"] == "info"


def test_build_quality_checks_non_date_text_column_not_flagged():
	dataframe = pd.DataFrame(
		{
			"category": ["alpha", "beta", "gamma", "delta", "epsilon"],
		}
	)

	checks = build_quality_checks(dataframe)
	date_findings = [f for f in checks["findings"] if f["check_name"] == "Possible Date Column"]

	assert date_findings == []


def test_build_quality_checks_suspicious_mixed_type_column_finding():
	dataframe = pd.DataFrame(
		{
			"mixed_value": ["100", "200", "300", "alpha", "beta", "gamma"],
		}
	)

	checks = build_quality_checks(dataframe)
	mixed_findings = [
		f for f in checks["findings"] if f["check_name"] == "Suspicious Mixed-Type Column"
	]

	assert len(mixed_findings) == 1
	assert mixed_findings[0]["column_name"] == "mixed_value"
	assert mixed_findings[0]["severity"] == "warning"
	assert "numeric-like" in mixed_findings[0]["message"]
	assert "text-like" in mixed_findings[0]["message"]
	assert "evaluated rows" in mixed_findings[0]["message"]


def test_build_quality_checks_all_numeric_like_text_column_not_flagged():
	dataframe = pd.DataFrame(
		{
			"numeric_text": ["10", "20", "30", "40", "50", "60"],
		}
	)

	checks = build_quality_checks(dataframe)
	mixed_findings = [
		f for f in checks["findings"] if f["check_name"] == "Suspicious Mixed-Type Column"
	]

	assert mixed_findings == []


def test_build_quality_checks_all_text_column_not_flagged():
	dataframe = pd.DataFrame(
		{
			"category": ["alpha", "beta", "gamma", "delta", "epsilon", "zeta"],
		}
	)

	checks = build_quality_checks(dataframe)
	mixed_findings = [
		f for f in checks["findings"] if f["check_name"] == "Suspicious Mixed-Type Column"
	]

	assert mixed_findings == []


def test_build_quality_checks_low_row_count_mixed_column_not_flagged():
	dataframe = pd.DataFrame(
		{
			"mixed_value": ["100", "alpha", "200", "beta"],
		}
	)

	checks = build_quality_checks(dataframe)
	mixed_findings = [
		f for f in checks["findings"] if f["check_name"] == "Suspicious Mixed-Type Column"
	]

	assert mixed_findings == []


def test_build_quality_checks_blank_strings_ignored_for_mixed_type_count():
	dataframe = pd.DataFrame(
		{
			"mixed_value": ["100", "200", "alpha", "beta", "gamma", " ", "", None],
		}
	)

	checks = build_quality_checks(dataframe)
	mixed_findings = [
		f for f in checks["findings"] if f["check_name"] == "Suspicious Mixed-Type Column"
	]

	assert len(mixed_findings) == 1
	assert mixed_findings[0]["column_name"] == "mixed_value"
	assert "across 5 evaluated rows" in mixed_findings[0]["message"]
