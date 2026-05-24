from __future__ import annotations

import pandas as pd


CSV_LOAD_ERROR_MESSAGE = "Unable to read CSV file. Please confirm the file is a valid CSV."
EXCEL_LOAD_ERROR_MESSAGE = "Unable to read Excel file. Please confirm the file is a valid Excel workbook."
EXCEL_SHEETS_ERROR_MESSAGE = "Unable to read Excel sheets. Please confirm the file is a valid Excel workbook."


def _rewind(file_obj: object) -> None:
	seek = getattr(file_obj, "seek", None)
	if callable(seek):
		seek(0)


def load_csv_file(uploaded_file: object) -> pd.DataFrame:
	_rewind(uploaded_file)

	try:
		return pd.read_csv(uploaded_file)
	except (pd.errors.ParserError, UnicodeDecodeError, ValueError) as exc:
		raise ValueError(CSV_LOAD_ERROR_MESSAGE) from exc
	except Exception as exc:
		raise ValueError(CSV_LOAD_ERROR_MESSAGE) from exc


def get_excel_sheet_names(uploaded_file: object) -> list[str]:
	_rewind(uploaded_file)

	try:
		return pd.ExcelFile(uploaded_file).sheet_names
	except Exception as exc:
		raise ValueError(EXCEL_SHEETS_ERROR_MESSAGE) from exc


def load_excel_file(uploaded_file: object, sheet_name: str | int = 0) -> pd.DataFrame:
	_rewind(uploaded_file)

	try:
		return pd.read_excel(uploaded_file, sheet_name=sheet_name)
	except Exception as exc:
		raise ValueError(EXCEL_LOAD_ERROR_MESSAGE) from exc
