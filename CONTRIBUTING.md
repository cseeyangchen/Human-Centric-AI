# Contributing

Thank you for helping keep Human-Centric AI Resources accurate and current.

## What to Submit

Please open an issue or pull request for:

- a missing paper, dataset, or benchmark;
- an incorrect title, venue, year, or category;
- a broken paper, project, code, or dataset link;
- a duplicate entry or a resource that has moved.
- a reusable practical tool or independently maintained learning hub.

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

For practical tools or learning hubs, replace the paper-specific fields with:

```text
Resource name:
Official URL:
Resource type: Practical Tool or Learning Hub
Primary workflow or learning scope:
Interface or learning format:
License and access notes:
Reason for inclusion:
```

## Category Guide

Method papers should use one of the fourteen categories under the six human context levels in `resources/awesome-human-centric-ai-survey-resources.md`. Datasets and benchmarks should follow the sixteen resource categories in the same file used in Chapter 7 of the survey.

When a work spans several categories, select its primary contribution and mention any secondary category in the pull-request description. Existing survey entries may remain in multiple categories when the manuscript explicitly discusses them in more than one context.

Practical tools should support a reusable research workflow beyond one paper implementation. Learning hubs should organize multiple concepts or exercises into a maintained self-study entry point. Formal multi-lecture courses belong under Open Courseware, while individual talks and tutorials belong under Academic Presentations.

## Repository Maintenance

The generated index is stored in `data/resources.json`. Link corrections that are not available in the survey tables are maintained in `data/link_overrides.json`. The README and resource pages can be regenerated locally with:

```bash
python3 scripts/build_readme.py --survey-root /path/to/survey/source
```

Please do not edit generated tables in `resources/awesome-human-centric-ai-survey-resources.md` without updating the corresponding structured source.

## Licensing Contributions

By submitting a contribution, you agree that it may be distributed under the
license applicable to the files you modify, as described in `LICENSE`:

- software contributions are licensed under the MIT License; and
- original documentation, resource descriptions, curated metadata, and
  authorized survey figures are licensed under CC BY 4.0.

Only submit material that you have the right to contribute. Identify any
third-party material and preserve its copyright, attribution, and license
notices.
