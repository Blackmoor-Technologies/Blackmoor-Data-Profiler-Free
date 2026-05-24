from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

from profiler.file_loader import get_excel_sheet_names, load_csv_file, load_excel_file
from profiler.quality_checks import build_quality_checks
from profiler.report_builder import build_markdown_report
from profiler.schema_profile import build_schema_profile


DISPLAY_COLUMN_NAMES = {
	"column_name": "Column",
	"inferred_dtype": "Inferred Type",
	"missing_count": "Missing Count",
	"missing_percent": "Missing %",
	"distinct_count": "Distinct Count",
	"sample_values": "Sample Values",
}

DISPLAY_FINDING_NAMES = {
	"check_name": "Check",
	"severity": "Severity",
	"column_name": "Column",
	"message": "Message",
}

APP_VERSION = "v1.0.0-baseline"

SAMPLE_FILE_OPTIONS = [
	"Use sample: customer_sample.csv",
	"Use sample: orders_sample.csv",
	"Use sample: excel_smoke_test.xlsx",
]


def _sample_file_path(sample_file_name: str) -> Path:
	return Path(__file__).resolve().parent / "sample_data" / sample_file_name


def _detect_file_type(file_name: str) -> str:
	suffix = Path(file_name).suffix.lower()
	if suffix == ".csv":
		return "CSV"
	if suffix in {".xls", ".xlsx"}:
		return "Excel"
	return "Unknown"


def _format_sample_values_for_display(value: object) -> str:
	if isinstance(value, list):
		if not value:
			return ""
		return ", ".join(str(item) for item in value)
	if value is None:
		return ""
	return str(value)


def _load_sample_data(sample_file_name: str, selected_sheet: str | None = None) -> tuple[pd.DataFrame, str, str, str | None]:
	sample_path = _sample_file_path(sample_file_name)
	file_type = _detect_file_type(sample_file_name)
	if file_type == "Excel":
		with sample_path.open("rb") as sample_file:
			sheet_names = get_excel_sheet_names(sample_file)
		if selected_sheet is None:
			selected_sheet = sheet_names[0]
		with sample_path.open("rb") as sample_file:
			dataframe = load_excel_file(sample_file, sheet_name=selected_sheet)
		return dataframe, sample_file_name, file_type, selected_sheet

	with sample_path.open("rb") as sample_file:
		dataframe = load_csv_file(sample_file)
	return dataframe, sample_file_name, file_type, None


def main() -> None:
	st.title("Blackmoor Data Profiler")
	st.caption("Local-first CSV and Excel profiling for analysts, builders, and small teams.")
	st.sidebar.write("Blackmoor Technologies")
	st.sidebar.write(f"Version: {APP_VERSION}")
	st.sidebar.header("About")
	st.sidebar.write("Local CSV/Excel data profiling tool.")
	st.sidebar.write("Uploaded files are processed locally in this running app session.")
	st.sidebar.write("Sample datasets are available in the sample_data folder.")
	st.sidebar.header("Current Features")
	st.sidebar.write("- CSV/Excel profiling")
	st.sidebar.write("- Data quality findings")
	st.sidebar.write("- Markdown report export")
	st.sidebar.write("- Local-only workflow")
	st.sidebar.header("Usage Notes")
	st.sidebar.write("- Local-first workflow")
	st.sidebar.write("- Use fictional or authorized data")
	st.sidebar.write("- Follow your organization’s data policies")

	data_source = st.radio(
		"Choose data source",
		["Upload my own file", *SAMPLE_FILE_OPTIONS],
	)

	if data_source == "Upload my own file":
		uploaded_file = st.file_uploader("Upload a CSV or Excel file", type=["csv", "xls", "xlsx"])
		if uploaded_file is None:
			st.info("Upload a CSV or Excel file to profile it locally.")
			return

		file_name = uploaded_file.name
		file_type = _detect_file_type(file_name)
		try:
			if file_type == "Excel":
				sheet_names = get_excel_sheet_names(uploaded_file)
				selected_sheet = st.selectbox("Select sheet", sheet_names)
				dataframe = load_excel_file(uploaded_file, sheet_name=selected_sheet)
			elif file_type == "CSV":
				selected_sheet = None
				dataframe = load_csv_file(uploaded_file)
			else:
				st.error("Unsupported file type. Please upload a CSV or Excel file.")
				return
		except ValueError as error:
			st.error(str(error))
			return
	else:
		sample_file_name = data_source.replace("Use sample: ", "")
		file_name = sample_file_name
		file_type = _detect_file_type(file_name)
		try:
			if file_type == "Excel":
				sample_path = _sample_file_path(sample_file_name)
				with sample_path.open("rb") as sample_file:
					sheet_names = get_excel_sheet_names(sample_file)
				selected_sheet = st.selectbox("Select sheet", sheet_names, key=f"sample-sheet-{sample_file_name}")
				dataframe, _, _, selected_sheet = _load_sample_data(sample_file_name, selected_sheet=selected_sheet)
			elif file_type == "CSV":
				selected_sheet = None
				dataframe, _, _, _ = _load_sample_data(sample_file_name)
			else:
				st.error("Unsupported file type. Please upload a CSV or Excel file.")
				return
		except ValueError as error:
			st.error(str(error))
			return

	profile = build_schema_profile(dataframe)
	quality_checks = build_quality_checks(dataframe)

	st.divider()
	st.subheader("Dataset Overview")
	overview_data: dict[str, object] = {
		"File name": file_name,
		"File type": file_type,
		"Row count": profile["row_count"],
		"Column count": profile["column_count"],
	}
	if selected_sheet is not None:
		overview_data["Selected sheet name"] = selected_sheet

	st.table(pd.DataFrame([overview_data]))

	st.divider()
	st.subheader("Column Profile")
	column_profile_df = pd.DataFrame(profile["columns"])
	if "sample_values" in column_profile_df.columns:
		column_profile_df["sample_values"] = column_profile_df["sample_values"].apply(
			_format_sample_values_for_display
		)
	column_profile_df = column_profile_df.rename(columns=DISPLAY_COLUMN_NAMES)
	st.dataframe(column_profile_df, use_container_width=True)

	st.divider()
	st.subheader("Data Quality Findings")
	st.caption("Quality findings are heuristic first-pass indicators and may require human review.")
	duplicate_count_col, duplicate_percent_col = st.columns(2)
	duplicate_count_col.metric("Duplicate row count", quality_checks["duplicate_row_count"])
	duplicate_percent_col.metric("Duplicate row percent", f"{quality_checks['duplicate_row_percent']}%")

	if quality_checks["findings"]:
		findings_df = pd.DataFrame(quality_checks["findings"])
		findings_df = findings_df.rename(columns=DISPLAY_FINDING_NAMES)
		st.dataframe(findings_df, use_container_width=True)
	else:
		st.success("No data quality findings for the current checks.")

	st.divider()

	markdown_report = build_markdown_report(
		profile=profile,
		quality_checks=quality_checks,
		file_name=file_name,
		file_type=file_type,
		selected_sheet=selected_sheet,
	)
	report_file_name = f"{Path(file_name).stem}_profile_report.md"
	st.download_button(
		label="Download Markdown Report",
		data=markdown_report,
		file_name=report_file_name,
		mime="text/markdown",
	)


if __name__ == "__main__":
	main()
