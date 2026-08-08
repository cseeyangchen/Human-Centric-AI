#!/usr/bin/env python3
"""Resolve missing paper pages through authoritative bibliographic indexes."""

from __future__ import annotations

import argparse
import difflib
import json
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path


USER_AGENT = "Human-Centric-AI-Resources/1.0 (mailto:cs-yang.chen@connect.polyu.hk)"


def normalized(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()


def similarity(left: str, right: str) -> float:
    left_norm, right_norm = normalized(left), normalized(right)
    sequence = difflib.SequenceMatcher(None, left_norm, right_norm).ratio()
    left_tokens, right_tokens = set(left_norm.split()), set(right_norm.split())
    jaccard = len(left_tokens & right_tokens) / max(1, len(left_tokens | right_tokens))
    return 0.7 * sequence + 0.3 * jaccard


def get_json(url: str) -> dict:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


def openalex_candidates(title: str) -> list[dict]:
    query = urllib.parse.urlencode(
        {
            "search": title,
            "per-page": 5,
            "mailto": "cs-yang.chen@connect.polyu.hk",
            "select": "id,doi,title,publication_year,primary_location,locations",
        }
    )
    payload = get_json(f"https://api.openalex.org/works?{query}")
    candidates = []
    for item in payload.get("results", []):
        url = item.get("doi")
        primary = item.get("primary_location") or {}
        if not url:
            url = primary.get("landing_page_url")
        if not url:
            for location in item.get("locations") or []:
                if location.get("landing_page_url"):
                    url = location["landing_page_url"]
                    break
        candidates.append(
            {
                "title": item.get("title") or "",
                "year": item.get("publication_year"),
                "url": url or item.get("id") or "",
                "source": "OpenAlex",
            }
        )
    return candidates


def crossref_candidates(title: str) -> list[dict]:
    query = urllib.parse.urlencode(
        {
            "query.bibliographic": title,
            "rows": 5,
            "select": "DOI,title,published-print,published-online,URL",
            "mailto": "cs-yang.chen@connect.polyu.hk",
        }
    )
    payload = get_json(f"https://api.crossref.org/works?{query}")
    candidates = []
    for item in payload.get("message", {}).get("items", []):
        candidate_title = (item.get("title") or [""])[0]
        date_parts = (
            (item.get("published-print") or {}).get("date-parts")
            or (item.get("published-online") or {}).get("date-parts")
            or [[None]]
        )
        year = date_parts[0][0] if date_parts and date_parts[0] else None
        doi = item.get("DOI")
        url = f"https://doi.org/{doi}" if doi else item.get("URL", "")
        candidates.append(
            {"title": candidate_title, "year": year, "url": url, "source": "Crossref"}
        )
    return candidates


def best_candidate(title: str, year: str) -> dict | None:
    candidates = []
    try:
        candidates.extend(openalex_candidates(title))
    except Exception as error:
        print(f"OpenAlex warning: {error}")
    expected_year = int(year) if year.isdigit() else None
    scored = []
    for candidate in candidates:
        score = similarity(title, candidate["title"])
        if expected_year and candidate.get("year") and abs(expected_year - int(candidate["year"])) > 1:
            score -= 0.12
        scored.append((score, candidate))
    if not scored or max(scored, key=lambda item: item[0])[0] < 0.86:
        try:
            for candidate in crossref_candidates(title):
                score = similarity(title, candidate["title"])
                if expected_year and candidate.get("year") and abs(expected_year - int(candidate["year"])) > 1:
                    score -= 0.12
                scored.append((score, candidate))
        except Exception as error:
            print(f"Crossref warning: {error}")
    if not scored:
        return None
    score, candidate = max(scored, key=lambda item: item[0])
    if score < 0.86 or not candidate.get("url"):
        return None
    candidate["confidence"] = round(score, 4)
    return candidate


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    repo_root = args.repo_root.resolve()
    index = json.loads((repo_root / "data" / "resources.json").read_text(encoding="utf-8"))
    output_path = repo_root / "data" / "link_overrides.json"
    overrides = json.loads(output_path.read_text(encoding="utf-8")) if output_path.exists() else {}

    records = {}
    for group in index["datasets_and_benchmarks"].values():
        for rows in group.values():
            for row in rows:
                records[row["bibkey"]] = row
    missing = [key for key in index["audit"]["resource_entries_without_paper_url"] if key not in overrides]
    unresolved = []
    for position, key in enumerate(missing, start=1):
        record = records[key]
        print(f"[{position}/{len(missing)}] {key}: {record['title']}")
        candidate = best_candidate(record["title"], record.get("year", ""))
        if candidate:
            overrides[key] = {
                "paper_url": candidate["url"],
                "matched_title": candidate["title"],
                "source": candidate["source"],
                "confidence": candidate["confidence"],
            }
            print(f"  -> {candidate['url']} ({candidate['confidence']})")
        else:
            unresolved.append(key)
            print("  -> unresolved")
        time.sleep(0.11)

    output_path.write_text(json.dumps(overrides, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"resolved": len(overrides), "unresolved": unresolved}, indent=2))


if __name__ == "__main__":
    main()
