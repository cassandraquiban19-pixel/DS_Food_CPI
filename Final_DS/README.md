# Food Prices Across the Philippines — Streamlit Dashboard

A clean white-and-green interactive dashboard for exploring Philippine Food CPI patterns from 2018–2025.

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Included files
- `app.py` — Streamlit dashboard
- `MLDST_Final_Cleaned.csv` — final cleaned dataset
- `philippines_regions.geojson` — local regional boundaries for the watermark-free map
- `requirements.txt` — Python dependencies

## Visual styling
The Food Category Change and Regional Change charts both use a single forest-green shade (`#2F7D4A`) rather than a fading gradient. Other dashboard colors and functionality are retained.
