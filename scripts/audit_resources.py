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
        "awesome research": repo_root / "resources" / "awesome-research.md",
        "survey resources": repo_root / "resources" / "awesome-human-centric-ai-survey-resources.md",
        "workshop collections": repo_root / "resources" / "workshop-collections.md",
    }
    markdown: dict[str, str] = {}
    for label, path in markdown_paths.items():
        if not path.is_file():
            errors.append(f"Missing generated Markdown page: {path.relative_to(repo_root)}")
            markdown[label] = ""
        else:
            markdown[label] = path.read_text(encoding="utf-8")
    required_infrastructure_pages = [
        "resources/human-models-and-toolkits.md",
        "resources/practical-tools.md",
        "resources/simulation-and-evaluation.md",
    ]
    for relative in required_infrastructure_pages:
        if not (repo_root / relative).is_file():
            errors.append(f"Missing infrastructure page: {relative}")
    readme = markdown["README"]
    research_lists = markdown["awesome research"]
    survey_resources = markdown["survey resources"]
    workshops = markdown["workshop collections"]
    papers = survey_resources.split('<a id="paper-resources"></a>', 1)[-1].split(
        '<a id="datasets-and-benchmarks"></a>', 1
    )[0]
    datasets = survey_resources.split('<a id="datasets-and-benchmarks"></a>', 1)[-1]

    method_source_keys: set[str] = set()
    for relative in build_readme.METHOD_SECTION_FILES + build_readme.METHOD_TABLE_FILES:
        method_source_keys.update(active_citations(survey_root / relative))
    supplemental_path = repo_root / "data" / "supplemental_methods.json"
    supplemental_methods = (
        json.loads(supplemental_path.read_text(encoding="utf-8"))
        if supplemental_path.exists()
        else []
    )
    supplemental_method_keys = {entry["bibkey"] for entry in supplemental_methods}
    expected_method_keys = method_source_keys | supplemental_method_keys
    method_index_keys = {
        record["bibkey"]
        for level in index["method_papers"].values()
        for records in level.values()
        for record in records
    }
    if expected_method_keys != method_index_keys:
        errors.append(
            "Method coverage mismatch: missing={} extra={}".format(
                sorted(expected_method_keys - method_index_keys),
                sorted(method_index_keys - expected_method_keys),
            )
        )

    supplemental_perspectives_path = repo_root / "data" / "supplemental_perspectives.json"
    supplemental_perspectives = (
        json.loads(supplemental_perspectives_path.read_text(encoding="utf-8"))
        if supplemental_perspectives_path.exists()
        else []
    )
    expected_perspective_keys = {entry["bibkey"] for entry in supplemental_perspectives}
    perspective_index_keys = {
        record["bibkey"]
        for group in index["perspective_papers"].values()
        for records in group.values()
        for record in records
    }
    if expected_perspective_keys != perspective_index_keys:
        errors.append(
            "Perspective coverage mismatch: missing={} extra={}".format(
                sorted(expected_perspective_keys - perspective_index_keys),
                sorted(perspective_index_keys - expected_perspective_keys),
            )
        )

    evaluation = build_readme.strip_comments(
        (survey_root / "sections/7_evaluation.tex").read_text(encoding="utf-8")
    )
    evaluation = evaluation.split("\\subsection{Metrics}", 1)[0]
    resource_source_keys = set(build_readme.citation_keys(evaluation))
    for relative in build_readme.DATA_TABLE_CATEGORY:
        resource_source_keys.update(active_citations(survey_root / relative))
    supplemental_resources_path = repo_root / "data" / "supplemental_resources.json"
    supplemental_resources = (
        json.loads(supplemental_resources_path.read_text(encoding="utf-8"))
        if supplemental_resources_path.exists()
        else []
    )
    supplemental_resource_keys = {entry["bibkey"] for entry in supplemental_resources}
    expected_resource_keys = resource_source_keys | supplemental_resource_keys
    resource_index_keys = {
        record["bibkey"]
        for group in index["datasets_and_benchmarks"].values()
        for records in group.values()
        for record in records
    }
    if expected_resource_keys != resource_index_keys:
        errors.append(
            "Resource coverage mismatch: missing={} extra={}".format(
                sorted(expected_resource_keys - resource_index_keys),
                sorted(resource_index_keys - expected_resource_keys),
            )
        )

    all_records = [
        record
        for level in index["method_papers"].values()
        for records in level.values()
        for record in records
    ] + [
        record
        for group in index["perspective_papers"].values()
        for records in group.values()
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

    expected_method_rows = (
        index["summary"]["categorized_method_entries"]
        + index["summary"]["categorized_perspective_entries"]
    )
    expected_resource_rows = index["summary"]["categorized_resource_entries"]
    expected_rows = expected_method_rows + expected_resource_rows
    paper_icon = "[:page_facing_up:]("
    if papers.count(paper_icon) != expected_method_rows:
        errors.append(
            "Paper-resource row/link mismatch: expected {}, found {}".format(
                expected_method_rows, papers.count(paper_icon)
            )
        )
    if datasets.count(paper_icon) != expected_resource_rows:
        errors.append(
            "Dataset-resource row/link mismatch: expected {}, found {}".format(
                expected_resource_rows, datasets.count(paper_icon)
            )
        )
    if paper_icon in readme:
        errors.append("README still contains generated resource rows")

    required_resource_links = [
        "#academic-knowledge",
        "#research-infrastructure",
        "#community-learning-hubs",
        "resources/awesome-research.md",
        "resources/workshop-collections.md",
        "resources/open-courseware.md",
        "resources/academic-presentations.md",
        "resources/human-models-and-toolkits.md",
        "resources/practical-tools.md",
        "resources/simulation-and-evaluation.md",
    ]
    for link in required_resource_links:
        if link not in readme:
            errors.append(f"README resource navigation is missing link: {link}")

    expected_method_details = (
        len(build_readme.METHOD_LEVELS)
        + sum(len(categories) for categories in build_readme.METHOD_LEVELS.values())
        + len(build_readme.PERSPECTIVE_GROUPS)
        + sum(len(categories) for categories in build_readme.PERSPECTIVE_GROUPS.values())
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
    ) + sum(
        len(categories) for categories in build_readme.PERSPECTIVE_GROUPS.values()
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

    expected_method_tables = sum(
        len(categories) for categories in build_readme.METHOD_LEVELS.values()
    )
    expected_perspective_tables = sum(
        len(categories) for categories in build_readme.PERSPECTIVE_GROUPS.values()
    )
    if papers.count("| Method | Paper | Venue | Paper Page | Website |") != expected_method_tables:
        errors.append("Paper-resource table count does not match the taxonomy")
    if (
        papers.count("| Perspective | Paper | Venue | Paper Page | Website |")
        != expected_perspective_tables
    ):
        errors.append("Perspective table count does not match the configured categories")
    if datasets.count("| Resource | Type | Venue | Paper | Paper Page | Website |") != sum(
        len(categories) for categories in build_readme.DATA_GROUPS.values()
    ):
        errors.append("Dataset-resource table count does not match Chapter 7 organization")

    required_root_links = [
        "resources/awesome-research.md",
        "resources/workshop-collections.md",
        "resources/human-models-and-toolkits.md",
        "resources/practical-tools.md",
        "resources/simulation-and-evaluation.md",
    ]
    for link in required_root_links:
        if link not in readme:
            errors.append(f"README is missing resource-page link: {link}")
    expected_research_lists = [
        (name, url)
        for resources in build_readme.AWESOME_RESEARCH_LISTS.values()
        for name, url, _ in resources
    ]
    research_list_rows = re.findall(r"^- \*\*(.+?)\*\*:", research_lists, re.MULTILINE)
    if len(research_list_rows) != len(expected_research_lists):
        errors.append(
            "Research-list row mismatch: expected {}, found {}".format(
                len(expected_research_lists), len(research_list_rows)
            )
        )
    for name, url in expected_research_lists:
        if f"**{name}**" not in research_lists or f"]({url})" not in research_lists:
            errors.append(f"Research-list page is missing entry or link: {name}")
    if research_lists.count('<a href="../README.md">') < 2:
        errors.append("Research lists are missing top or bottom README navigation")
    if survey_resources.count('<a href="../README.md">') < 2:
        errors.append("Survey resources are missing top or bottom README navigation")
    workshop_urls = re.findall(r"\]\((https?://[^)]+)\)", workshops)
    generic_workshop_urls = sorted(
        {
            url
            for url in workshop_urls
            if not build_readme.has_direct_workshop_page("", "", url)
        }
    )
    if generic_workshop_urls:
        errors.append(
            f"Workshop page contains conference-wide directory links: {generic_workshop_urls}"
        )
    if "unsolvedsocialnav.org" in workshops:
        errors.append("Workshop page contains a domain that no longer hosts the listed event")
    if workshops.count('<a href="../README.md">') < 2:
        errors.append("Workshop resources are missing top or bottom README navigation")
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
        "method_source_papers": len(expected_method_keys),
        "method_index_papers": len(method_index_keys),
        "perspective_source_papers": len(expected_perspective_keys),
        "perspective_index_papers": len(perspective_index_keys),
        "resource_source_entries": len(expected_resource_keys),
        "resource_index_entries": len(resource_index_keys),
        "categorized_markdown_rows": expected_rows,
        "verified_workshop_links": len(workshop_urls),
        "errors": errors,
    }
    print(json.dumps(report, indent=2))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
