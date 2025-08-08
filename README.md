# OSINT Link Analysis Toolkit (Compliant Scaffold)

This project provides a compliant, semi-automated workflow to investigate potential online connections between two subjects using only publicly available information and platform-compliant methods.

Important: This scaffold prioritizes ethics, legality, and platform Terms of Service. It deliberately avoids scraping login-protected content and disables facial recognition by default.

## Ethic-Legal Principles
- Use only public, consensually available data. Respect robots.txt and platform ToS.
- Do not harass, stalk, dox, or attempt unauthorized access. You are responsible for lawful use in your jurisdiction.
- Facial recognition is disabled by default and must only be used where you have the legal right and consent to do so, and with API providers that authorize your use case.

## Features
- Public web and image discovery via DuckDuckGo search API wrapper (no headless scraping required)
- Image harvesting with metadata capture (URL, source, timestamps)
- Graph/network analysis of public footprints and domains (NetworkX)
- Markdown report generation with supporting evidence (links, screenshots placeholders, metadata)
- Modular CLI that can be extended with APIs (e.g., Bing, SerpAPI, Azure)

## Non-Goals / Guardrails
- No automated scraping behind logins or bypassing paywalls.
- No automation of sites that prohibit scraping.
- No built-in biometric processing without explicit opt-in and credentials.

## Setup
1. Python 3.10+
2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
3. Copy the environment template and add API keys if you plan to enable optional providers:
   ```bash
   cp .env.example .env
   ```
4. (Optional) Edit `config.yaml` to set defaults.

## CLI Overview
```
python main.py --help
```

Key commands:
- `init` — Creates data directories for two subjects.
- `collect` — Public web search + image harvesting for a subject.
- `analyze` — Builds a lightweight graph of public sources and overlaps.
- `report` — Generates a Markdown report with links and evidence.
- `face-search` — Disabled by default. Requires explicit opt-in via env and provider keys.

## Example Workflow
1. Initialize folders for aliasable subjects (replace with pseudonyms or internal IDs):
   ```bash
   python main.py init --subject-a "subject_a" --subject-b "subject_b"
   ```
2. Collect public images and links for each subject (tune queries and limits):
   ```bash
   python main.py collect --subject "subject_a" --query "\"First Last\" city keyword" --limit 50
   python main.py collect --subject "subject_b" --query "\"First Last\" company keyword" --limit 50
   ```
3. Analyze overlaps (domains, repeated handles, co-mentions in result snippets):
   ```bash
   python main.py analyze --subject-a "subject_a" --subject-b "subject_b"
   ```
4. Generate a report:
   ```bash
   python main.py report --subject-a "subject_a" --subject-b "subject_b" --out reports/case_001.md
   ```

## Enabling Facial Recognition (Optional, Off by Default)
- Set `ALLOW_FACIAL_RECOGNITION=true` in `.env`.
- Provide keys for a compliant API that authorizes your use case. Some providers restrict FR to vetted customers or specific use cases. This toolkit will refuse to run FR if keys or opt-in are missing.
- Read provider terms carefully before use.

## Data Locations
- `data/raw/<subject>/images/` — downloaded images
- `data/raw/<subject>/metadata/` — JSONL with result metadata
- `data/processed/` — derived artifacts (graphs, tables)
- `reports/` — generated outputs

## Extending
- Add collectors under `osint_tool/collectors/` for specific APIs.
- Add resolvers/matchers under `osint_tool/analysis/` to enrich link analysis.
- Add templates to `osint_tool/reporting/templates/` to customize reports.

## Disclaimer
This repository is for lawful OSINT and investigative research with public data. You are solely responsible for ensuring compliance with all applicable laws, regulations, and platform terms.