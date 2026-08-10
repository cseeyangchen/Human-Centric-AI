#!/usr/bin/env python3
"""Audit source coverage and generated Markdown structure."""

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
    errors: list[str] = []
    markdown_paths = {
        "README": repo_root / "README.md",
        "paper resources": repo_root / "resources" / "papers.md",
        "datasets and benchmarks": repo_root / "resources" / "datasets-and-benchmarks.md",
    }
    markdown: dict[str, str] = {}
    for label, path in markdown_paths.items():
        if not path.is_file():
            errors.append(f"Missing generated Markdown page: {path.relative_to(repo_root)}")
            markdown[label] = ""
        else:
            markdown[label] = path.read_text(encoding="utf-8")
    readme = markdown["README"]
    papers = markdown["paper resources"]
    datasets = markdown["datasets and benchmarks"]

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

    expected_method_rows = index["summary"]["categorized_method_entries"]
    expected_resource_rows = index["summary"]["categorized_resource_entries"]
    expected_rows = expected_method_rows + expected_resource_rows
    if papers.count("[Paper](") != expected_method_rows:
        errors.append(
            "Paper-resource row/link mismatch: expected {}, found {}".format(
                expected_method_rows, papers.count("[Paper](")
            )
        )
    if datasets.count("[Paper](") != expected_resource_rows:
        errors.append(
            "Dataset-resource row/link mismatch: expected {}, found {}".format(
                expected_resource_rows, datasets.count("[Paper](")
            )
        )
    if "[Paper](" in readme:
        errors.append("README still contains generated resource rows")

    expected_method_details = len(build_readme.METHOD_LEVELS) + sum(
        len(categories) for categories in build_readme.METHOD_LEVELS.values()
    )
    expected_resource_details = len(build_readme.DATA_GROUPS) + sum(
        len(categories) for categories in build_readme.DATA_GROUPS.values()
    )
    if papers.count("<details>") != expected_method_details:
        errors.append("Paper resources do not contain the expected collapsed blocks")
    if datasets.count("<details>") != expected_resource_details:
        errors.append("Datasets and benchmarks do not contain the expected collapsed blocks")
    expected_nested_method_details = sum(
        len(categories) for categories in build_readme.METHOD_LEVELS.values()
    )
    expected_nested_resource_details = sum(
        len(categories) for categories in build_readme.DATA_GROUPS.values()
    )
    if papers.count("> <details>") != expected_nested_method_details:
        errors.append("Paper subcategory blocks are not consistently nested")
    if datasets.count("> <details>") != expected_nested_resource_details:
        errors.append("Dataset subcategory blocks are not consistently nested")
    for label, content in (("paper resources", papers), ("datasets and benchmarks", datasets)):
        if "<details open" in content:
            errors.append(f"{label.title()} contains a details block that is open by default")
        if content.count("<details>") != content.count("</details>"):
            errors.append(f"{label.title()} contains unbalanced details blocks")

    if papers.count("| Paper | Venue | Paper Page | Website |") != sum(
        len(categories) for categories in build_readme.METHOD_LEVELS.values()
    ):
        errors.append("Paper-resource table count does not match the taxonomy")
    if datasets.count("| Resource | Type | Year | Paper | Paper Page | Website |") != sum(
        len(categories) for categories in build_readme.DATA_GROUPS.values()
    ):
        errors.append("Dataset-resource table count does not match Chapter 7 organization")

    required_root_links = [
        "[📚 **Paper Resources**](resources/papers.md)",
        "[🗃️ **Datasets and Benchmarks**](resources/datasets-and-benchmarks.md)",
    ]
    for link in required_root_links:
        if link not in readme:
            errors.append(f"README is missing resource-page link: {link}")
    if papers.count('<a href="../README.md">') < 2:
        errors.append("Paper resources are missing top or bottom README navigation")
    if datasets.count('<a href="../README.md">') < 2:
        errors.append("Datasets and benchmarks are missing top or bottom README navigation")
    required_images = [
        "assets/survey-overview.png",
        "assets/human-centric-resources-logo-v4.png",
        *build_readme.METHOD_LEVEL_ICONS.values(),
        *build_readme.DATA_GROUP_ICONS.values(),
    ]
    for image in required_images:
        if not (repo_root / image).is_file():
            errors.append(f"Missing resource image: {image}")
    for image in build_readme.METHOD_LEVEL_ICONS.values():
        if f'../{image}' not in papers:
            errors.append(f"Paper resources do not reference expected icon: {image}")
    for image in build_readme.DATA_GROUP_ICONS.values():
        if f'../{image}' not in datasets:
            errors.append(f"Datasets and benchmarks do not reference expected icon: {image}")

    report = {
        "method_source_papers": len(method_source_keys),
        "method_index_papers": len(method_index_keys),
        "resource_source_entries": len(resource_source_keys),
        "resource_index_entries": len(resource_index_keys),
        "categorized_markdown_rows": expected_rows,
        "errors": errors,
    }
    print(json.dumps(report, indent=2))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
