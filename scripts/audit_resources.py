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
        "surveys": repo_root / "resources" / "surveys.md",
        "perspectives": repo_root / "resources" / "perspectives.md",
        "workshop collections": repo_root / "resources" / "workshop-collections.md",
    }
    for level in build_readme.METHOD_LEVELS:
        markdown_paths[f"method level: {level}"] = (
            repo_root / "resources" / build_readme.method_level_filename(level)
        )
    for group in build_readme.DATA_GROUPS:
        markdown_paths[f"data group: {group}"] = (
            repo_root / "resources" / build_readme.data_group_filename(group)
        )
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
    surveys_and_perspectives = "\n".join(
        [markdown["surveys"], markdown["perspectives"]]
    )
    method_level_pages = {
        level: markdown[f"method level: {level}"]
        for level in build_readme.METHOD_LEVELS
    }
    papers = "\n".join(method_level_pages.values())
    data_group_pages = {
        group: markdown[f"data group: {group}"]
        for group in build_readme.DATA_GROUPS
    }
    datasets = "\n".join(data_group_pages.values())

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

    intro_survey_keys = build_readme.introduction_survey_citations(
        survey_root / build_readme.INTRODUCTION_FILE
    )
    supplemental_surveys_path = repo_root / "data" / "supplemental_surveys.json"
    supplemental_surveys = (
        json.loads(supplemental_surveys_path.read_text(encoding="utf-8"))
        if supplemental_surveys_path.exists()
        else []
    )
    supplemental_survey_keys = {entry["bibkey"] for entry in supplemental_surveys}
    expected_survey_keys = intro_survey_keys | supplemental_survey_keys
    survey_index_keys = {record["bibkey"] for record in index["survey_papers"]}
    if expected_survey_keys != survey_index_keys:
        errors.append(
            "Survey coverage mismatch: missing={} extra={}".format(
                sorted(expected_survey_keys - survey_index_keys),
                sorted(survey_index_keys - expected_survey_keys),
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
    ] + index["survey_papers"] + [
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

    chronological_groups = []
    for level, categories in index["method_papers"].items():
        for category, records in categories.items():
            chronological_groups.append((f"{level} / {category}", records))
    for group, categories in index["datasets_and_benchmarks"].items():
        for category, records in categories.items():
            chronological_groups.append((f"{group} / {category}", records))
    chronological_groups.append(("Surveys", index["survey_papers"]))
    for group, categories in index["perspective_papers"].items():
        for category, records in categories.items():
            chronological_groups.append((f"{group} / {category}", records))
    for label, records in chronological_groups:
        expected_order = sorted(records, key=build_readme.record_sort_key)
        if [record["bibkey"] for record in records] != [
            record["bibkey"] for record in expected_order
        ]:
            errors.append(f"Resource table is not newest-first: {label}")

    expected_method_rows = index["summary"]["categorized_method_entries"]
    expected_context_rows = (
        index["summary"]["categorized_perspective_entries"]
        + index["summary"]["categorized_survey_entries"]
    )
    expected_resource_rows = index["summary"]["categorized_resource_entries"]
    expected_rows = expected_context_rows + expected_method_rows + expected_resource_rows
    paper_icon = "[:page_facing_up:]("
    if surveys_and_perspectives.count(paper_icon) != expected_context_rows:
        errors.append(
            "Survey-and-perspective row/link mismatch: expected {}, found {}".format(
                expected_context_rows, surveys_and_perspectives.count(paper_icon)
            )
        )
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
    if paper_icon in survey_resources:
        errors.append("Survey index should link to dedicated pages instead of duplicating rows")

    required_resource_links = [
        "resources/awesome-human-centric-ai-survey-resources.md",
        *[
            f"resources/{build_readme.method_level_filename(level)}"
            for level in build_readme.METHOD_LEVELS
        ],
        "resources/awesome-research.md",
        "resources/workshop-collections.md",
        "resources/learning-hubs.md",
        "resources/open-courseware.md",
        "resources/academic-presentations.md",
        "resources/human-models-and-toolkits.md",
        "resources/practical-tools.md",
        "resources/simulation-and-evaluation.md",
    ]
    for link in required_resource_links:
        if link not in readme:
            errors.append(f"README resource navigation is missing link: {link}")

    for label, content in (
        ("surveys and perspectives", surveys_and_perspectives),
        ("method resources", papers),
        ("datasets and benchmarks", datasets),
    ):
        if "<details" in content:
            errors.append(f"{label.title()} should expose its dedicated-page content directly")

    expected_method_tables = sum(
        len(categories) for categories in build_readme.METHOD_LEVELS.values()
    )
    expected_perspective_tables = sum(
        len(categories) for categories in build_readme.PERSPECTIVE_GROUPS.values()
    )
    if papers.count("| Method | Paper | Venue | Paper Page | Website |") != expected_method_tables:
        errors.append("Paper-resource table count does not match the taxonomy")
    for level, categories in build_readme.METHOD_LEVELS.items():
        level_page = method_level_pages[level]
        level_filename = build_readme.method_level_filename(level)
        if f'href="{level_filename}"' not in survey_resources:
            errors.append(f"Survey index is missing method-level link: {level_filename}")
        if level_page.count("| Method | Paper | Venue | Paper Page | Website |") != len(categories):
            errors.append(f"Method page table count does not match categories: {level}")
        for category in categories:
            if f'<a id="{build_readme.anchor(category)}"></a>' not in level_page:
                errors.append(f"Method page is missing category anchor: {level} / {category}")
        if '<a href="../README.md">' not in level_page:
            errors.append(f"Method page is missing README navigation: {level}")
        if 'href="awesome-human-centric-ai-survey-resources.md"' not in level_page:
            errors.append(f"Method page is missing survey-index navigation: {level}")
    if (
        surveys_and_perspectives.count("| Perspective | Paper | Venue | Paper Page | Website |")
        != expected_perspective_tables
    ):
        errors.append("Perspective table count does not match the configured categories")
    if surveys_and_perspectives.count("| Survey | Paper | Venue | Paper Page | Website |") != 1:
        errors.append("Survey table count does not match the configured survey section")
    if datasets.count("| Resource | Type | Venue | Paper | Paper Page | Website |") != sum(
        len(categories) for categories in build_readme.DATA_GROUPS.values()
    ):
        errors.append("Dataset-resource table count does not match Chapter 7 organization")
    for group, categories in build_readme.DATA_GROUPS.items():
        group_page = data_group_pages[group]
        group_filename = build_readme.data_group_filename(group)
        if f'href="{group_filename}"' not in survey_resources:
            errors.append(f"Survey index is missing dataset-group link: {group_filename}")
        if group_page.count("| Resource | Type | Venue | Paper | Paper Page | Website |") != len(categories):
            errors.append(f"Dataset page table count does not match categories: {group}")
        for category in categories:
            if f'<a id="{build_readme.anchor(category)}"></a>' not in group_page:
                errors.append(f"Dataset page is missing category anchor: {group} / {category}")
        if '<a href="../README.md">' not in group_page:
            errors.append(f"Dataset page is missing README navigation: {group}")
        if 'href="awesome-human-centric-ai-survey-resources.md"' not in group_page:
            errors.append(f"Dataset page is missing survey-index navigation: {group}")
    for filename in ("surveys.md", "perspectives.md"):
        if f'href="{filename}"' not in survey_resources:
            errors.append(f"Survey index is missing context-page link: {filename}")

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
            errors.append(f"Method level pages do not reference expected icon: {image}")
    for image in build_readme.DATA_GROUP_ICONS.values():
        if f'../{image}' not in datasets:
            errors.append(f"Datasets and benchmarks do not reference expected icon: {image}")

    report = {
        "method_source_papers": len(expected_method_keys),
        "method_index_papers": len(method_index_keys),
        "perspective_source_papers": len(expected_perspective_keys),
        "perspective_index_papers": len(perspective_index_keys),
        "survey_source_papers": len(expected_survey_keys),
        "survey_index_papers": len(survey_index_keys),
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
