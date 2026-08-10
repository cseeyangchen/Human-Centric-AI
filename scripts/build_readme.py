#!/usr/bin/env python3
"""Build the Human-Centric AI Resources README from the survey sources.

The script treats the survey as the source of truth. It combines citations from
Chapters 4--6 with active rows in the method tables, and combines citations from
the dataset/benchmark discussion with active rows in the resource tables.
"""

from __future__ import annotations

import argparse
import html
import json
import re
import urllib.parse
from collections import OrderedDict
from datetime import date
from pathlib import Path
from typing import Iterable


# Set this after the survey is publicly available on arXiv. The badge is
# rendered without a link while the value is empty.
SURVEY_ARXIV_URL = ""
GITHUB_REPOSITORY = "cseeyangchen/Human-Centric-AI"
GITHUB_REPOSITORY_URL = f"https://github.com/{GITHUB_REPOSITORY}"
VISITOR_COUNTER_ID = "cseeyangchen-Human-Centric-AI"

ROMAN_NUMERALS = ("I", "II", "III", "IV", "V", "VI")

METHOD_LEVEL_ICONS = {
    "Visual Appearance": "assets/level-icons/visual-appearance.png",
    "Spatial Geometry": "assets/level-icons/spatial-geometry.png",
    "Kinematic Dynamics": "assets/level-icons/kinematic-dynamics.png",
    "Interaction Modeling": "assets/level-icons/interaction-modeling.png",
    "World Simulation": "assets/level-icons/world-simulation.png",
    "Embodied Agency": "assets/level-icons/embodied-agency.png",
}

DATA_GROUP_ICONS = {
    "Human Subject Resources": "assets/resource-icons/human-subject-resources.png",
    "Human Dynamics Resources": "assets/resource-icons/human-dynamics-resources.png",
    "Human Interaction Resources": "assets/resource-icons/human-interaction-resources.png",
    "Human Embodiment Resources": "assets/resource-icons/human-embodiment-resources.png",
}


METHOD_LEVELS = OrderedDict(
    [
        (
            "Visual Appearance",
            [
                "Generalist Human Perception",
                "Discriminative Identity Understanding",
                "Controllable Human Generation",
            ],
        ),
        (
            "Spatial Geometry",
            ["Structured Geometry Modeling", "Renderable Avatar Modeling"],
        ),
        (
            "Kinematic Dynamics",
            ["Scalable Motion Modeling", "Human Video Animation"],
        ),
        (
            "Interaction Modeling",
            [
                "Human-Object Interaction",
                "Human-Scene Interaction",
                "Social Interaction",
            ],
        ),
        (
            "World Simulation",
            ["Human-Centered World Generation", "Actionable World Planning"],
        ),
        (
            "Embodied Agency",
            ["Generalist Humanoid Control", "Human-to-Agent Skill Transfer"],
        ),
    ]
)

METHOD_SECTION_FILES = [
    "sections/4_appearance_geometry.tex",
    "sections/5_dynamics_interaction.tex",
    "sections/6_world_embodied.tex",
]

METHOD_TABLE_FILES = [
    "tables/summary_4_appearance_geometry.tex",
    "tables/summary_5_dynamics.tex",
    "tables/summary_5_interaction.tex",
    "tables/summary_6_world_embodied.tex",
]

DATA_GROUPS = OrderedDict(
    [
        (
            "Human Subject Resources",
            [
                "Visual Human Observation",
                "Multisensory Human Sensing",
                "Human Identity Understanding",
                "Renderable Human Geometry",
            ],
        ),
        (
            "Human Dynamics Resources",
            [
                "Human Video Generation and Animation",
                "Human Video Behavior Understanding",
                "Human Kinematic Motion Resources",
                "Human Gait Understanding",
                "Sport Analysis",
                "Virtual Try-On",
            ],
        ),
        (
            "Human Interaction Resources",
            [
                "Egocentric Procedural Activities",
                "Human-Object Interaction Data",
                "Human-Scene Interaction Data",
                "Social Interaction Data",
            ],
        ),
        (
            "Human Embodiment Resources",
            ["Human Data for Embodied AI", "Physical Humanoid Control"],
        ),
    ]
)

DATA_TABLE_CATEGORY = {
    "tables/summary_7_db_renderable.tex": "Renderable Human Geometry",
    "tables/summary_7_db_motion.tex": "Human Kinematic Motion Resources",
    "tables/summary_7_db_egocentric.tex": "Egocentric Procedural Activities",
    "tables/summary_7_db_embodied.tex": "Human Data for Embodied AI",
}

CITE_RE = re.compile(r"\\cite[a-zA-Z]*\s*(?:\[[^\]]*\]\s*)*\{([^}]+)\}")
HREF_RE = re.compile(r"\\href\{([^}]+)\}\{[^}]*\}")
RESOURCE_META_RE = re.compile(
    r"\|\s*(Dataset\+Benchmark|Dataset|Benchmark)\s*\|\s*([^|]+?)\s*\|"
)


def strip_comments(text: str) -> str:
    lines = []
    for line in text.splitlines():
        cut = None
        for index, char in enumerate(line):
            if char == "%" and (index == 0 or line[index - 1] != "\\"):
                cut = index
                break
        lines.append(line if cut is None else line[:cut])
    return "\n".join(lines)


def citation_keys(text: str) -> list[str]:
    keys: list[str] = []
    for match in CITE_RE.finditer(text):
        keys.extend(key.strip() for key in match.group(1).split(",") if key.strip())
    return keys


def parse_bibtex(path: Path) -> dict[str, dict[str, str]]:
    text = path.read_text(encoding="utf-8")
    entries: dict[str, dict[str, str]] = {}
    cursor = 0
    while True:
        match = re.search(r"@(\w+)\s*\{\s*([^,\s]+)\s*,", text[cursor:], re.S)
        if not match:
            break
        entry_type, key = match.group(1).lower(), match.group(2)
        body_start = cursor + match.end()
        depth = 1
        index = body_start
        quoted = False
        escaped = False
        while index < len(text) and depth:
            char = text[index]
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                quoted = not quoted
            elif not quoted and char == "{":
                depth += 1
            elif not quoted and char == "}":
                depth -= 1
            index += 1
        body = text[body_start : index - 1]
        fields: dict[str, str] = {"ENTRYTYPE": entry_type, "ID": key}
        field_cursor = 0
        while field_cursor < len(body):
            field_match = re.search(r"([A-Za-z][\w-]*)\s*=\s*", body[field_cursor:])
            if not field_match:
                break
            field = field_match.group(1).lower()
            value_start = field_cursor + field_match.end()
            if value_start >= len(body):
                break
            opener = body[value_start]
            if opener == "{":
                value_depth = 1
                value_index = value_start + 1
                escaped = False
                while value_index < len(body) and value_depth:
                    char = body[value_index]
                    if escaped:
                        escaped = False
                    elif char == "\\":
                        escaped = True
                    elif char == "{":
                        value_depth += 1
                    elif char == "}":
                        value_depth -= 1
                    value_index += 1
                value = body[value_start + 1 : value_index - 1]
            elif opener == '"':
                value_index = value_start + 1
                escaped = False
                while value_index < len(body):
                    char = body[value_index]
                    if escaped:
                        escaped = False
                    elif char == "\\":
                        escaped = True
                    elif char == '"':
                        value_index += 1
                        break
                    value_index += 1
                value = body[value_start + 1 : value_index - 1]
            else:
                value_index = value_start
                while value_index < len(body) and body[value_index] not in ",\n":
                    value_index += 1
                value = body[value_start:value_index]
            fields[field] = value.strip()
            field_cursor = value_index
        entries[key] = fields
        cursor = index
    return entries


def latex_to_text(value: str) -> str:
    value = value.strip()
    while len(value) >= 2 and value[0] == "{" and value[-1] == "}":
        value = value[1:-1].strip()
    replacements = {
        r"\\&": "&",
        r"\\_": "_",
        r"\\%": "%",
        r"\\#": "#",
        "~": " ",
        "--": "-",
    }
    for old, new in replacements.items():
        value = value.replace(old, new)
    value = re.sub(r"\\(?:textit|textbf|emph|mathrm|mathbf|mathit)\{([^{}]*)\}", r"\1", value)
    value = re.sub(r"\\(?:em|sc)\s+", "", value)
    value = value.replace("$", "")
    value = value.replace("{", "").replace("}", "")
    value = re.sub(r"\\[A-Za-z]+", "", value)
    value = re.sub(r"\s+", " ", value)
    return value.strip()


def split_cells(row: str) -> list[str]:
    return [cell.strip() for cell in re.split(r"(?<!\\)&", row)]


def clean_row_name(cell: str) -> str:
    cell = CITE_RE.sub("", cell)
    cell = re.sub(r"\\rowcolor\{[^}]+\}", "", cell)
    cell = re.sub(r"\\textsuperscript\{([^}]+)\}", r"\1", cell)
    cell = re.sub(r"\\(?:textbf|textit)\{([^{}]+)\}", r"\1", cell)
    return latex_to_text(cell).strip()


def row_metadata(row: str, resource_type: str | None = None, meta_venue: str | None = None) -> dict:
    cells = split_cells(row)
    keys = citation_keys(row)
    if not keys or len(cells) < 3:
        return {}
    paper_links = HREF_RE.findall(cells[-2]) if len(cells) >= 2 else []
    web_links = HREF_RE.findall(cells[-1]) if cells else []
    return {
        "keys": keys,
        "name": clean_row_name(cells[0]),
        "venue": latex_to_text(cells[1]),
        "paper_links": paper_links,
        "web_links": web_links,
        "resource_type": resource_type,
        "meta_venue": latex_to_text(meta_venue or ""),
    }


def parse_active_table(path: Path, known_categories: Iterable[str]) -> tuple[dict[str, set[str]], dict[str, dict]]:
    categories = {name: set() for name in known_categories}
    metadata: dict[str, dict] = {}
    current_category: str | None = None
    pending_type: str | None = None
    pending_venue: str | None = None
    buffer: list[str] = []

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        stripped = raw_line.lstrip()
        if stripped.startswith("%"):
            meta_match = RESOURCE_META_RE.search(stripped)
            if meta_match:
                pending_type = meta_match.group(1).replace("+", " + ")
                pending_venue = meta_match.group(2).strip()
            continue
        line = strip_comments(raw_line).strip()
        if not line:
            continue
        for category in known_categories:
            if category in line and "Sec.~\\ref" in line:
                current_category = category
                break
        buffer.append(line)
        if "\\\\" not in line:
            continue
        row = " ".join(buffer)
        buffer = []
        parsed = row_metadata(row, pending_type, pending_venue)
        if not parsed:
            continue
        for key in parsed["keys"]:
            metadata[key] = merge_metadata(metadata.get(key), parsed)
            if current_category:
                categories[current_category].add(key)
        pending_type = None
        pending_venue = None
    return categories, metadata


def parse_all_table_rows(path: Path) -> dict[str, dict]:
    """Parse active and commented-out table rows to recover links for prose citations."""
    metadata: dict[str, dict] = {}
    row_buffer: list[str] = []
    collecting = False
    pending_type: str | None = None
    pending_venue: str | None = None

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        stripped = raw_line.lstrip()
        meta_match = RESOURCE_META_RE.search(stripped)
        if meta_match:
            pending_type = meta_match.group(1).replace("+", " + ")
            pending_venue = meta_match.group(2).strip()
        if stripped.startswith("%"):
            normalized = re.sub(r"^%+\s?", "", stripped)
        else:
            normalized = strip_comments(raw_line).strip()
        if not collecting and CITE_RE.search(normalized) and "&" in normalized:
            collecting = True
            row_buffer = [normalized]
        elif collecting:
            row_buffer.append(normalized)
        if collecting and "\\\\" in normalized:
            parsed = row_metadata(" ".join(row_buffer), pending_type, pending_venue)
            for key in parsed.get("keys", []):
                metadata[key] = merge_metadata(metadata.get(key), parsed)
            collecting = False
            row_buffer = []
            pending_type = None
            pending_venue = None
    return metadata


def merge_metadata(existing: dict | None, incoming: dict) -> dict:
    if not existing:
        return {
            "name": incoming.get("name", ""),
            "venue": incoming.get("venue", ""),
            "paper_links": list(incoming.get("paper_links", [])),
            "web_links": list(incoming.get("web_links", [])),
            "resource_type": incoming.get("resource_type"),
            "meta_venue": incoming.get("meta_venue", ""),
        }
    merged = dict(existing)
    for field in ("name", "venue", "resource_type", "meta_venue"):
        if not merged.get(field) and incoming.get(field):
            merged[field] = incoming[field]
    for field in ("paper_links", "web_links"):
        merged[field] = list(dict.fromkeys(merged.get(field, []) + incoming.get(field, [])))
    return merged


def extract_subsubsection_citations(path: Path, allowed: set[str]) -> tuple[dict[str, set[str]], set[str]]:
    text = strip_comments(path.read_text(encoding="utf-8"))
    matches = list(re.finditer(r"\\subsubsection\{([^}]+)\}", text))
    result = {name: set() for name in allowed}
    assigned: set[str] = set()
    for index, match in enumerate(matches):
        title = latex_to_text(match.group(1))
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        if title not in allowed:
            continue
        keys = set(citation_keys(text[match.end() : end]))
        result[title].update(keys)
        assigned.update(keys)
    return result, set(citation_keys(text)) - assigned


def extract_marked_citations(text: str, markers: list[str], end_marker: str | None = None) -> dict[str, set[str]]:
    clean = strip_comments(text)
    end_limit = clean.find(end_marker) if end_marker and end_marker in clean else len(clean)
    positions: list[tuple[int, str, int]] = []
    for marker in markers:
        token = f"\\textbf{{{marker}.}}"
        position = clean.find(token)
        if position < 0:
            raise ValueError(f"Could not find dataset category marker: {marker}")
        positions.append((position, marker, position + len(token)))
    positions.sort()
    result: dict[str, set[str]] = {}
    for index, (_, marker, content_start) in enumerate(positions):
        candidates = [end_limit]
        if index + 1 < len(positions):
            candidates.append(positions[index + 1][0])
        next_subsubsection = clean.find("\\subsubsection{", content_start)
        if next_subsubsection >= 0:
            candidates.append(next_subsubsection)
        content_end = min(candidate for candidate in candidates if candidate >= content_start)
        result[marker] = set(citation_keys(clean[content_start:content_end]))
    return result


def bib_paper_url(entry: dict[str, str]) -> str:
    url = latex_to_text(entry.get("url", ""))
    if url.startswith("http"):
        return url
    doi = latex_to_text(entry.get("doi", ""))
    if doi:
        return doi if doi.startswith("http") else f"https://doi.org/{doi}"
    eprint = latex_to_text(entry.get("eprint", ""))
    if re.fullmatch(r"\d{4}\.\d{4,5}(v\d+)?", eprint):
        return f"https://arxiv.org/abs/{eprint}"
    journal = latex_to_text(entry.get("journal", ""))
    arxiv_match = re.search(r"arXiv[: ](\d{4}\.\d{4,5})", journal, re.I)
    if arxiv_match:
        return f"https://arxiv.org/abs/{arxiv_match.group(1)}"
    return ""


def venue_name(entry: dict[str, str]) -> str:
    raw = latex_to_text(entry.get("booktitle") or entry.get("journal") or "")
    lower = raw.lower()
    mappings = [
        ("computer vision and pattern recognition", "CVPR"),
        ("international conference on computer vision", "ICCV"),
        ("european conference on computer vision", "ECCV"),
        ("neural information processing systems", "NeurIPS"),
        ("learning representations", "ICLR"),
        ("machine learning", "ICML"),
        ("artificial intelligence", "AAAI"),
        ("robotics and automation", "ICRA"),
        ("intelligent robots and systems", "IROS"),
        ("computer graphics and interactive techniques", "SIGGRAPH"),
        ("multimedia", "ACM MM"),
    ]
    for needle, short in mappings:
        if needle in lower:
            return short
    if lower.startswith("arxiv"):
        return "arXiv"
    return raw


def normalize_venue(table_venue: str, entry: dict[str, str]) -> str:
    year = latex_to_text(entry.get("year", ""))
    venue = table_venue.strip()
    venue = venue.replace("'", " ")
    venue = re.sub(r"\s+", " ", venue).strip()
    if venue and venue not in {"NA", "Not Mentioned"}:
        if re.search(r"\b\d{2}\b", venue):
            venue = re.sub(r"\b(\d{2})\b", lambda match: f"20{match.group(1)}", venue, count=1)
        if re.search(r"\b\d{2,4}\b", venue):
            return venue
        return f"{venue} {year}".strip()
    fallback = venue_name(entry)
    return f"{fallback} {year}".strip() or year or "-"


def title_prefix(title: str) -> str:
    if ":" in title:
        prefix = title.split(":", 1)[0].strip()
        if 1 <= len(prefix.split()) <= 8 and len(prefix) <= 70:
            return prefix
    return title


def infer_resource_type(title: str, explicit: str | None) -> str:
    if explicit:
        return explicit
    lower = title.lower()
    has_dataset = "dataset" in lower or "data set" in lower
    has_benchmark = "benchmark" in lower
    if has_dataset and has_benchmark:
        return "Dataset + Benchmark"
    if has_benchmark:
        return "Benchmark"
    return "Dataset"


def website_links(links: Iterable[str]) -> list[dict[str, str]]:
    result = []
    seen = set()
    for url in (link for link in links if link.startswith("http")):
        canonical = url.rstrip("/").removesuffix(".git").lower()
        if canonical in seen:
            continue
        seen.add(canonical)
        host = urllib.parse.urlparse(url).netloc.lower()
        label = "Code" if "github.com" in host or "gitlab" in host else "Project"
        result.append({"label": label, "url": url})
    return result


def build_record(key: str, bib: dict[str, dict[str, str]], metadata: dict[str, dict], resource: bool) -> dict:
    entry = bib.get(key, {})
    meta = metadata.get(key, {})
    title = latex_to_text(entry.get("title", "")) or meta.get("name") or key
    paper_links = meta.get("paper_links", [])
    paper_url = paper_links[0] if paper_links else bib_paper_url(entry)
    year = latex_to_text(entry.get("year", ""))
    table_venue = meta.get("meta_venue") if resource and meta.get("meta_venue") else meta.get("venue", "")
    record = {
        "bibkey": key,
        "title": title,
        "year": year,
        "venue": normalize_venue(table_venue or "", entry),
        "paper_url": paper_url,
        "websites": website_links(meta.get("web_links", [])),
    }
    if resource:
        record["name"] = meta.get("name") or title_prefix(title)
        record["type"] = infer_resource_type(title, meta.get("resource_type"))
    return record


def record_sort_key(record: dict) -> tuple[int, str]:
    year_match = re.search(r"\d{4}", record.get("year", ""))
    year = int(year_match.group()) if year_match else 0
    return (-year, record.get("title", "").lower())


def md_escape(value: str) -> str:
    return html.escape(value, quote=False).replace("|", "\\|").replace("\n", " ")


def paper_link(url: str) -> str:
    return f"[Paper]({url})" if url else "-"


def web_link_cell(websites: list[dict[str, str]]) -> str:
    if not websites:
        return "-"
    return " / ".join(f"[{item['label']}]({item['url']})" for item in websites)


def method_table(records: list[dict]) -> str:
    lines = [
        "| Paper | Venue | Paper Page | Website |",
        "|---|:---:|:---:|:---:|",
    ]
    for record in records:
        lines.append(
            "| {title} | {venue} | {paper} | {website} |".format(
                title=md_escape(record["title"]),
                venue=md_escape(record["venue"]),
                paper=paper_link(record["paper_url"]),
                website=web_link_cell(record["websites"]),
            )
        )
    return "\n".join(lines)


def resource_table(records: list[dict]) -> str:
    lines = [
        "| Resource | Type | Year | Paper | Paper Page | Website |",
        "|---|:---:|:---:|---|:---:|:---:|",
    ]
    for record in records:
        lines.append(
            "| {name} | {type} | {year} | {title} | {paper} | {website} |".format(
                name=md_escape(record["name"]),
                type=md_escape(record["type"]),
                year=md_escape(record["year"] or "-"),
                title=md_escape(record["title"]),
                paper=paper_link(record["paper_url"]),
                website=web_link_cell(record["websites"]),
            )
        )
    return "\n".join(lines)


def anchor(text: str) -> str:
    return re.sub(r"[^a-z0-9 -]", "", text.lower()).replace(" ", "-")


def blockquote(markdown: str) -> str:
    """Indent a generated Markdown block while preserving nested rendering."""
    return "\n".join(f"> {line}" if line else ">" for line in markdown.splitlines())


def render_readme(index: dict) -> str:
    arxiv_badge_image = '<img src="https://img.shields.io/badge/arXiv-Survey-B31B1B?logo=arxiv&logoColor=white" alt="arXiv">'
    arxiv_badge = arxiv_badge_image
    if SURVEY_ARXIV_URL:
        arxiv_badge = f'<a href="{SURVEY_ARXIV_URL}">{arxiv_badge_image}</a>'

    badge_line = " ".join(
        [
            '<a href="https://awesome.re"><img src="https://img.shields.io/badge/Awesome-fc60a8?logo=awesomelists&logoColor=white" alt="Awesome"></a>',
            '<a href="https://cseeyangchen.github.io/Human-Centric-AI/homepage/"><img src="https://img.shields.io/badge/Homepage-2f766f?logo=homeassistant&logoColor=white" alt="Homepage"></a>',
            f'<img src="https://komarev.com/ghpvc/?username={VISITOR_COUNTER_ID}&label=Visitors&color=2563eb&style=flat" alt="Visitors">',
            f'<a href="{GITHUB_REPOSITORY_URL}/stargazers"><img src="https://img.shields.io/github/stars/{GITHUB_REPOSITORY}?label=Stars&logo=github&color=f59e0b" alt="Stars"></a>',
            f'<a href="{GITHUB_REPOSITORY_URL}/forks"><img src="https://img.shields.io/github/forks/{GITHUB_REPOSITORY}?label=Forks&logo=github&color=0f766e" alt="Forks"></a>',
            arxiv_badge,
            '<a href="CONTRIBUTING.md"><img src="https://img.shields.io/badge/PRs-welcome-brightgreen.svg" alt="PRs Welcome"></a>',
            f'<a href="{GITHUB_REPOSITORY_URL}/commits/main"><img src="https://img.shields.io/github/last-commit/{GITHUB_REPOSITORY}?label=Last%20updated&color=64748b" alt="Last updated"></a>',
        ]
    )

    lines = [
        '<h1 align="center"><img src="assets/human-centric-resources-logo-v4.png" width="58" height="58" align="absmiddle" alt="Human-Centric AI Resources logo">&nbsp; Human-Centric AI Resources</h1>',
        "",
        '<p align="center"><b>An open, community-driven hub for human-centric AI.</b></p>',
        "",
        f'<p align="center">{badge_line}</p>',
        "",
        '<p align="center">',
        '  <img src="assets/survey-overview.png" width="100%" alt="Overview of Human-Centric Intelligence in the Era of Foundation Models">',
        "</p>",
        "",
        "This repository is organized around the six-level framework introduced in **Human-Centric Intelligence in the Era of Foundation Models: A Survey**. Beyond preserving the survey bibliography, it is intended as an evolving community resource for discovering research artifacts and tracking new progress in human-centric AI.",
        "",
        '<a id="news"></a>',
        "",
        "## 📢 News",
        "",
        "- **2026-08-08:** Initial resource release with complete Chapter 4--7 coverage.",
        "",
        "## 🧭 Contents",
        "",
        "- [News](#news)",
        "- [Paper Resources](#paper-resources)",
        "- [Datasets and Benchmarks](#datasets-and-benchmarks)",
        "- [Contributing](#contributing)",
        "",
        '<a id="paper-resources"></a>',
        "",
        "## 📚 Paper Resources",
        "",
        "The paper index contains the union of works cited in the Chapter 4--6 method discussions and works listed in the corresponding method tables. Each level and subcategory is collapsed by default for faster navigation.",
        "",
    ]

    for level_number, (level, categories) in enumerate(METHOD_LEVELS.items(), start=1):
        level_records = index["method_papers"][level]
        level_index = ROMAN_NUMERALS[level_number - 1]
        level_icon = METHOD_LEVEL_ICONS[level]
        lines.extend(
            [
                "<details>",
                f'<summary><img src="{level_icon}" width="28" height="28" align="absmiddle" alt=""> &nbsp; <b>{level_index}. {level}</b></summary>',
                "",
            ]
        )
        for category_number, category in enumerate(categories, start=1):
            records = level_records[category]
            category_block = "\n".join(
                [
                    "<details>",
                    f"<summary><b>{level_index}.{category_number}</b> &nbsp; {category}</summary>",
                    "",
                    method_table(records),
                    "",
                    "</details>",
                ]
            )
            lines.extend(
                [
                    blockquote(category_block),
                    "",
                ]
            )
        lines.extend(["</details>", ""])

    lines.extend(
        [
            '<a id="datasets-and-benchmarks"></a>',
            "",
            "## 🗂️ Datasets and Benchmarks",
            "",
            "Resources follow the organization used in Chapter 7 of the survey. Each resource group and subcategory is collapsed by default, and duplicate BibTeX entries are removed within each table.",
            "",
        ]
    )
    for group_number, (group, categories) in enumerate(DATA_GROUPS.items(), start=1):
        group_index = ROMAN_NUMERALS[group_number - 1]
        group_icon = DATA_GROUP_ICONS[group]
        lines.extend(
            [
                "<details>",
                f'<summary><img src="{group_icon}" width="24" height="24" align="absmiddle" alt=""> &nbsp; <b>{group_index}. {group}</b></summary>',
                "",
            ]
        )
        for category_number, category in enumerate(categories, start=1):
            records = index["datasets_and_benchmarks"][group][category]
            category_block = "\n".join(
                [
                    "<details>",
                    f"<summary><b>{group_index}.{category_number}</b> &nbsp; {category}</summary>",
                    "",
                    resource_table(records),
                    "",
                    "</details>",
                ]
            )
            lines.extend(
                [
                    blockquote(category_block),
                    "",
                ]
            )
        lines.extend(["</details>", ""])

    lines.extend(
        [
            '<a id="contributing"></a>',
            "",
            "## 🤝 Contributing",
            "",
            "Corrections and additions are welcome. Please open an issue or pull request and include the paper title, category, publication venue, paper page, and project or code link. See [CONTRIBUTING.md](CONTRIBUTING.md) for the expected format.",
            "",
        ]
    )

    citation_lines = [
        '<a id="citation"></a>',
        "",
        "## ✍️ Citation",
        "",
        "If this resource collection is useful in your research, please cite the accompanying survey:",
        "",
        "```bibtex",
        "@misc{chen2026humancentricintelligence,",
        "  title  = {Human-Centric Intelligence in the Era of Foundation Models: A Survey},",
        "  author = {Chen, Yang and Wang, Tianqi and Jiang, Xiaorui and Man, Yilei and",
        "            Shao, Yihua and Guo, Chuan and Liu, Mengyuan and Chen, Zhi and",
        "            Cao, Xiaofeng and Zhao, Qibin and Sebe, Nicu and Tao, Dacheng and",
        "            Zhou, Jingren and Zomaya, Albert Y. and Guo, Song and Guo, Jingcai},",
        "  year   = {2026},",
        "  note   = {Survey manuscript},",
        f"  url    = {{{GITHUB_REPOSITORY_URL}}}",
        "}",
        "```",
        "",
    ]
    lines.extend(["<!--", *citation_lines, "-->", ""])

    lines.extend(
        [
            "## 🙏 Acknowledgment",
            "",
            "This repository indexes third-party research artifacts. Copyright and licenses remain with the original authors and project maintainers.",
            "",
            "---",
            "",
            '<p align="center">',
            '  <strong>⭐ If this project helps you, please give us a Star!</strong><br>',
            '  <sub>Curated and maintained by <a href="https://lumen-lab-polyu.github.io/"><strong>Lumen Lab</strong></a> @ <a href="https://www.polyu.edu.hk/"><strong>The Hong Kong Polytechnic University</strong></a></sub>',
            "</p>",
            "",
        ]
    )
    return "\n".join(lines)


def build_index(survey_root: Path, overrides: dict[str, dict] | None = None) -> dict:
    bib = parse_bibtex(survey_root / "reference.bib")
    method_categories = {category for categories in METHOD_LEVELS.values() for category in categories}
    data_categories = {category for categories in DATA_GROUPS.values() for category in categories}

    all_table_metadata: dict[str, dict] = {}
    for relative in METHOD_TABLE_FILES + list(DATA_TABLE_CATEGORY):
        for key, meta in parse_all_table_rows(survey_root / relative).items():
            all_table_metadata[key] = merge_metadata(all_table_metadata.get(key), meta)
    method_keys = {category: set() for category in method_categories}
    unassigned_method_citations: dict[str, list[str]] = {}
    for relative in METHOD_SECTION_FILES:
        extracted, unassigned = extract_subsubsection_citations(survey_root / relative, method_categories)
        for category, keys in extracted.items():
            method_keys[category].update(keys)
        if unassigned:
            unassigned_method_citations[relative] = sorted(unassigned)

    for relative in METHOD_TABLE_FILES:
        active, active_meta = parse_active_table(survey_root / relative, method_categories)
        for category, keys in active.items():
            method_keys[category].update(keys)
        for key, meta in active_meta.items():
            all_table_metadata[key] = merge_metadata(all_table_metadata.get(key), meta)

    evaluation_text = (survey_root / "sections/7_evaluation.tex").read_text(encoding="utf-8")
    data_keys = extract_marked_citations(
        evaluation_text,
        [category for categories in DATA_GROUPS.values() for category in categories],
        end_marker="\\subsection{Metrics}",
    )
    for relative, category in DATA_TABLE_CATEGORY.items():
        active, active_meta = parse_active_table(survey_root / relative, data_categories)
        row_keys = set()
        for keys in active.values():
            row_keys.update(keys)
        # Resource tables do not contain subsection group headers; all active rows
        # belong to the category selected by the surrounding Chapter 7 discussion.
        if not row_keys:
            row_keys.update(active_meta)
        data_keys[category].update(row_keys)
        for key, meta in active_meta.items():
            merged = merge_metadata(all_table_metadata.get(key), meta)
            # In the dataset index, the resource-table label and Dataset/Benchmark
            # annotation are more specific than a method name from Chapters 4--6.
            for field in ("name", "resource_type", "meta_venue"):
                if meta.get(field):
                    merged[field] = meta[field]
            all_table_metadata[key] = merged

    # Explicit corrections are applied last so that verified resource names and
    # links can refine automatically parsed table metadata without touching TeX.
    for key, override in (overrides or {}).items():
        override_meta = {
            "paper_links": [override["paper_url"]] if override.get("paper_url") else [],
            "web_links": override.get("websites", []),
            "name": override.get("name", ""),
            "venue": override.get("venue", ""),
            "resource_type": override.get("type"),
            "meta_venue": override.get("venue", ""),
        }
        merged = merge_metadata(all_table_metadata.get(key), override_meta)
        for field in ("name", "resource_type", "venue", "meta_venue"):
            if override_meta.get(field):
                merged[field] = override_meta[field]
        all_table_metadata[key] = merged

    missing_bib = sorted(
        {
            key
            for keys in list(method_keys.values()) + list(data_keys.values())
            for key in keys
            if key not in bib
        }
    )

    method_output: dict[str, dict[str, list[dict]]] = OrderedDict()
    for level, categories in METHOD_LEVELS.items():
        method_output[level] = OrderedDict()
        for category in categories:
            records = [build_record(key, bib, all_table_metadata, False) for key in method_keys[category]]
            method_output[level][category] = sorted(records, key=record_sort_key)

    data_output: dict[str, dict[str, list[dict]]] = OrderedDict()
    for group, categories in DATA_GROUPS.items():
        data_output[group] = OrderedDict()
        for category in categories:
            records = [build_record(key, bib, all_table_metadata, True) for key in data_keys[category]]
            data_output[group][category] = sorted(records, key=record_sort_key)

    unique_method = {key for keys in method_keys.values() for key in keys}
    unique_data = {key for keys in data_keys.values() for key in keys}
    unresolved_paper_links = sorted(
        record["bibkey"]
        for level in method_output.values()
        for records in level.values()
        for record in records
        if not record["paper_url"]
    )
    unresolved_resource_links = sorted(
        record["bibkey"]
        for group in data_output.values()
        for records in group.values()
        for record in records
        if not record["paper_url"]
    )

    return {
        "generated_on": date.today().isoformat(),
        "summary": {
            "unique_method_papers": len(unique_method),
            "categorized_method_entries": sum(len(keys) for keys in method_keys.values()),
            "unique_resources": len(unique_data),
            "categorized_resource_entries": sum(len(keys) for keys in data_keys.values()),
        },
        "method_papers": method_output,
        "datasets_and_benchmarks": data_output,
        "audit": {
            "missing_bib_entries": missing_bib,
            "unassigned_method_citations": unassigned_method_citations,
            "method_entries_without_paper_url": unresolved_paper_links,
            "resource_entries_without_paper_url": unresolved_resource_links,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--survey-root", type=Path, required=True)
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    overrides_path = repo_root / "data" / "link_overrides.json"
    overrides = json.loads(overrides_path.read_text(encoding="utf-8")) if overrides_path.exists() else {}
    index = build_index(args.survey_root.resolve(), overrides)
    (repo_root / "data").mkdir(parents=True, exist_ok=True)
    (repo_root / "data" / "resources.json").write_text(
        json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (repo_root / "README.md").write_text(render_readme(index), encoding="utf-8")
    print(json.dumps(index["summary"], indent=2))
    print(json.dumps(index["audit"], indent=2))


if __name__ == "__main__":
    main()
