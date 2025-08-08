# OSINT Connection Analysis Pipeline

This project helps establish a potential connection between two individuals by:
- Collecting images from publicly available sources
- Running facial recognition to discover other appearances online
- Analyzing online footprints to find overlapping networks
- Producing an evidence-backed HTML report and graph exports

## Features
- DuckDuckGo image search for names/usernames
- Instagram public content collection (via `instaloader`)
- Optional Azure Face API verification (Detect + Verify)
- Perceptual-hash image de-duplication
- Network graph generation (NetworkX, GraphML export)
- HTML report with links, screenshots, and metadata

## Quickstart

1) Create and activate a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
```

2) Install dependencies

```bash
pip install -r requirements.txt
```

3) Configure environment variables (optional, for Azure Face API)

Copy `.env.example` to `.env` and set:
- `AZURE_FACE_ENDPOINT` (e.g., https://<your-region>.api.cognitive.microsoft.com/face/v1.0)
- `AZURE_FACE_KEY`

4) Prepare a config file

See `sample_config.yaml` and adapt for your subjects.

5) Run the pipeline

```bash
python -m osint.cli --config sample_config.yaml --output-dir ./outputs
```

This will: download images, verify faces (if Azure is configured), build a network graph and generate an HTML report in `./outputs`.

## Notes
- Respect platform terms of service and local laws. Only use publicly available data and avoid intrusive actions.
- Instagram collection requires public profiles. Private accounts are not accessible without login (not supported here).
- For visual link analysis, import the exported GraphML into tools like Gephi or Maltego.

## Structure

```
osint/
  cli.py
  pipeline.py
  config.py
  utils.py
  image_store.py
  scrapers/
    web_search.py
    instagram_public.py
  face/
    azure_face.py
    local_hash.py
  graph/
    graph_builder.py
  report/
    report_builder.py
    templates/
      report.html.j2
```