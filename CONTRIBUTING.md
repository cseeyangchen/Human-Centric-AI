# Contributing

Thank you for helping keep Human-Centric AI Resources accurate and current.

## What to Submit

Please open an issue or pull request for:

- a missing paper, dataset, or benchmark;
- an incorrect title, venue, year, or category;
- a broken paper, project, code, or dataset link;
- a duplicate entry or a resource that has moved.

## Required Information

Include the following information for each proposed entry:

```text
Title:
BibTeX key, if available:
Category:
Venue and year:
Paper page:
Project page:
Code or dataset page:
Reason for inclusion or correction:
```

## Category Guide

Method papers should use one of the fourteen categories under the six human context levels in `resources/awesome-human-centric-ai-survey-resources.md`. Datasets and benchmarks should follow the sixteen resource categories in the same file used in Chapter 7 of the survey.

When a work spans several categories, select its primary contribution and mention any secondary category in the pull-request description. Existing survey entries may remain in multiple categories when the manuscript explicitly discusses them in more than one context.

## Repository Maintenance

The generated index is stored in `data/resources.json`. Link corrections that are not available in the survey tables are maintained in `data/link_overrides.json`. The README and resource pages can be regenerated locally with:

```bash
python3 scripts/build_readme.py --survey-root /path/to/survey/source
```

Please do not edit generated tables in `resources/awesome-human-centric-ai-survey-resources.md` without updating the corresponding structured source.
