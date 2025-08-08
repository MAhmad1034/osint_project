# OSINT Connection Analysis Pipeline

This project helps establish a potential connection between two individuals by:
- Collecting images from publicly available sources
- Running facial recognition to discover other appearances online
- Analyzing online footprints to find overlapping networks
- Producing an evidence-backed HTML report and graph exports

## Features
- DuckDuckGo image search for names/usernames
- Instagram public content collection (via `instaloader`)
- Face recognition providers:
  - Local ONNX ArcFace (free; default) — requires downloading an ONNX model file
  - Local InsightFace (free; optional; may require build tools)
  - Local DeepFace (free; optional; requires TensorFlow on Windows)
  - Azure Face API (paid; optional)
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

3) Choose a face provider (free, default: local_onnx_arcface)

- Local ONNX ArcFace: download `arcfaceresnet100-8.onnx` and place it at `data/models/arcfaceresnet100-8.onnx`.
  You can obtain it from public ArcFace ONNX conversions or model zoos. Ensure the path matches the config.
- To switch providers, edit `sample_config.yaml` `face.provider` to one of:
  - `local_onnx_arcface` (default)
  - `local_insightface` (optional, requires onnxruntime and possibly build tools)
  - `local_deepface` (optional, requires TensorFlow)
  - `azure` (set `AZURE_FACE_ENDPOINT` and `AZURE_FACE_KEY` in `.env`)

4) Configure environment variables for Azure only (optional)

Copy `.env.example` to `.env` and set:
- `AZURE_FACE_ENDPOINT`
- `AZURE_FACE_KEY`

5) Prepare a config file

See `sample_config.yaml` and adapt for your subjects.

6) Run the pipeline

```bash
python -m osint.cli --config sample_config.yaml --output-dir ./outputs
```

This will: download images, verify faces (using your selected provider), build a network graph and generate an HTML report in `./outputs`.

## Notes
- Respect platform terms of service and local laws.
- Instagram collection requires public profiles.
- Import GraphML into tools like Gephi or Maltego.

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