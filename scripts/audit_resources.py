#!/usr/bin/env python3
"""Audit source coverage and generated README structure."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import build_readme


def active_citations(path: Path) -> set[str]:
    return set(build_readme.citation_keys(build_readme.strip_comments(path.read_text(encoding="utf-8"))))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--survey-root", type=Path, required=True)
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    survey_root = args.survey_root.resolve()
    repo_root = args.repo_root.resolve()
    index = json.loads((repo_root / "data" / "resources.json").read_text(encoding="utf-8"))
    readme = (repo_root / "README.md").read_text(encoding="utf-8")
    errors: list[str] = []

    method_source_keys: set[str] = set()
    for relative in build_readme.METHOD_SECTION_FILES + build_readme.METHOD_TABLE_FILES:
        method_source_keys.update(active_citations(survey_root / relative))
    method_index_keys = {
        record["bibkey"]
        for level in index["method_papers"].values()
        for records in level.values()
        for record in records
    }
    if method_source_keys != method_index_keys:
        errors.append(
            "Method coverage mismatch: missing={} extra={}".format(
                sorted(method_source_keys - method_index_keys),
                sorted(method_index_keys - method_source_keys),
            )
        )

    evaluation = build_readme.strip_comments(
        (survey_root / "sections/7_evaluation.tex").read_text(encoding="utf-8")
    )
    evaluation = evaluation.split("\\subsection{Metrics}", 1)[0]
    resource_source_keys = set(build_readme.citation_keys(evaluation))
    for relative in build_readme.DATA_TABLE_CATEGORY:
        resource_source_keys.update(active_citations(survey_root / relative))
    resource_index_keys = {
        record["bibkey"]
        for group in index["datasets_and_benchmarks"].values()
        for records in group.values()
        for record in records
    }
    if resource_source_keys != resource_index_keys:
        errors.append(
            "Resource coverage mismatch: missing={} extra={}".format(
                sorted(resource_source_keys - resource_index_keys),
                sorted(resource_index_keys - resource_source_keys),
            )
        )

    all_records = [
        record
        for level in index["method_papers"].values()
        for records in level.values()
        for record in records
    ] + [
        record
        for group in index["datasets_and_benchmarks"].values()
        for records in group.values()
        for record in records
    ]
    no_paper_page = sorted(record["bibkey"] for record in all_records if not record["paper_url"])
    invalid_paper_page = sorted(
        record["bibkey"] for record in all_records if not record["paper_url"].startswith(("http://", "https://"))
    )
    if no_paper_page:
        errors.append(f"Entries without paper page: {no_paper_page}")
    if invalid_paper_page:
        errors.append(f"Entries with invalid paper page: {invalid_paper_page}")

    expected_rows = index["summary"]["categorized_method_entries"] + index["summary"]["categorized_resource_entries"]
    if readme.count("[Paper](") != expected_rows:
        errors.append(
            f"README row/link mismatch: expected {expected_rows}, found {readme.count('[Paper](')}"
        )
    expected_details = len(build_readme.METHOD_LEVELS)
    expected_details += sum(len(categories) for categories in build_readme.METHOD_LEVELS.values())
    expected_details += len(build_readme.DATA_GROUPS)
    expected_details += sum(len(categories) for categories in build_readme.DATA_GROUPS.values())
    if readme.count("<details>") != expected_details:
        errors.append("README does not contain the expected level and subcategory collapsed blocks")
    expected_nested_details = sum(len(categories) for categories in build_readme.METHOD_LEVELS.values())
    expected_nested_details += sum(len(categories) for categories in build_readme.DATA_GROUPS.values())
    if readme.count("> <details>") != expected_nested_details:
        errors.append("README subcategory blocks are not consistently rendered at the nested level")
    if "<details open" in readme:
        errors.append("README contains a details block that is open by default")
    if readme.count("<details>") != readme.count("</details>"):
        errors.append("README contains unbalanced details blocks")
    if readme.count("| Paper | Venue | Paper Page | Website |") != sum(
        len(categories) for categories in build_readme.METHOD_LEVELS.values()
    ):
        errors.append("README method-table count does not match the taxonomy")
    if readme.count("| Resource | Type | Year | Paper | Paper Page | Website |") != sum(
        len(categories) for categories in build_readme.DATA_GROUPS.values()
    ):
        errors.append("README resource-table count does not match Chapter 7 organization")
    required_images = [
        "assets/survey-overview.png",
        "assets/human-centric-resources-logo-v4.png",
        *build_readme.METHOD_LEVEL_ICONS.values(),
        *build_readme.DATA_GROUP_ICONS.values(),
    ]
    for image in required_images:
        if not (repo_root / image).is_file():
            errors.append(f"Missing README image: {image}")

    report = {
        "method_source_papers": len(method_source_keys),
        "method_index_papers": len(method_index_keys),
        "resource_source_entries": len(resource_source_keys),
        "resource_index_entries": len(resource_index_keys),
        "categorized_readme_rows": expected_rows,
        "errors": errors,
    }
    print(json.dumps(report, indent=2))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
