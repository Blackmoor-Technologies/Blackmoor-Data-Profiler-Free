from io import BytesIO

import pandas as pd

import pytest

from profiler.file_loader import (
	CSV_LOAD_ERROR_MESSAGE,
	EXCEL_LOAD_ERROR_MESSAGE,
	EXCEL_SHEETS_ERROR_MESSAGE,
	get_excel_sheet_names,
	load_csv_file,
	load_excel_file,
)


def test_load_csv_file_returns_dataframe(tmp_path):
	csv_path = tmp_path / "sample.csv"
	csv_path.write_text("name,age\nAlice,30\nBob,25\n", encoding="utf-8")

	with csv_path.open("rb") as file_obj:
		dataframe = load_csv_file(file_obj)

	assert list(dataframe.columns) == ["name", "age"]
	assert dataframe.shape == (2, 2)
	assert dataframe.loc[0, "name"] == "Alice"


def test_load_excel_file_returns_selected_sheet(tmp_path):
	excel_path = tmp_path / "sample.xlsx"
	with pd.ExcelWriter(excel_path, engine="openpyxl") as writer:
		pd.DataFrame({"name": ["Alice", "Bob"]}).to_excel(writer, sheet_name="People", index=False)
		pd.DataFrame({"total": [10, 20]}).to_excel(writer, sheet_name="Totals", index=False)

	with excel_path.open("rb") as file_obj:
		sheet_names = get_excel_sheet_names(file_obj)

	assert sheet_names == ["People", "Totals"]

	with excel_path.open("rb") as file_obj:
		dataframe = load_excel_file(file_obj, sheet_name="Totals")

	assert list(dataframe.columns) == ["total"]
	assert dataframe.shape == (2, 1)
	assert dataframe.loc[0, "total"] == 10


def test_load_csv_file_invalid_content_raises_readable_value_error():
	with pytest.raises(ValueError, match=CSV_LOAD_ERROR_MESSAGE):
		load_csv_file(BytesIO(b"\x80\x81\x82"))


def test_load_excel_file_invalid_content_raises_readable_value_error():
	with pytest.raises(ValueError, match=EXCEL_LOAD_ERROR_MESSAGE):
		load_excel_file(BytesIO(b"not an excel workbook"))


def test_get_excel_sheet_names_invalid_content_raises_readable_value_error():
	with pytest.raises(ValueError, match=EXCEL_SHEETS_ERROR_MESSAGE):
		get_excel_sheet_names(BytesIO(b"not an excel workbook"))
