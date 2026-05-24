from __future__ import annotations

import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
	sys.path.insert(0, str(REPO_ROOT))

from profiler.file_loader import get_excel_sheet_names, load_csv_file, load_excel_file
from profiler.quality_checks import build_quality_checks
from profiler.report_builder import build_markdown_report
from profiler.schema_profile import build_schema_profile


SAMPLE_FILES = [
	"customer_sample.csv",
	"orders_sample.csv",
	"excel_smoke_test.xlsx",
]


def _detect_file_type(file_name: str) -> str:
	suffix = Path(file_name).suffix.lower()
	if suffix == ".csv":
		return "CSV"
	if suffix in {".xls", ".xlsx"}:
		return "Excel"
	return "Unknown"


def _load_sample_dataframe(sample_path: Path) -> tuple[object, str | None]:
	file_type = _detect_file_type(sample_path.name)
	if file_type == "Excel":
		with sample_path.open("rb") as sample_file:
			sheet_names = get_excel_sheet_names(sample_file)
		selected_sheet = sheet_names[0]
		with sample_path.open("rb") as sample_file:
			dataframe = load_excel_file(sample_file, sheet_name=selected_sheet)
		return dataframe, selected_sheet

	with sample_path.open("rb") as sample_file:
		dataframe = load_csv_file(sample_file)
	return dataframe, None


def main() -> None:
	sample_dir = REPO_ROOT / "sample_data"
	output_dir = REPO_ROOT / "reports" / "examples"
	output_dir.mkdir(parents=True, exist_ok=True)

	for sample_file_name in SAMPLE_FILES:
		sample_path = sample_dir / sample_file_name
		dataframe, selected_sheet = _load_sample_dataframe(sample_path)
		file_type = _detect_file_type(sample_file_name)

		profile = build_schema_profile(dataframe)
		quality_checks = build_quality_checks(dataframe)
		markdown_report = build_markdown_report(
			profile=profile,
			quality_checks=quality_checks,
			file_name=sample_file_name,
			file_type=file_type,
			selected_sheet=selected_sheet,
		)

		output_path = output_dir / f"{Path(sample_file_name).stem}_profile_report.md"
		output_path.write_text(markdown_report, encoding="utf-8")
		print(output_path)


if __name__ == "__main__":
	main()