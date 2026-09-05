# SciMantra Research Tools

A single Streamlit application containing laboratory calculators, research statistics,
environmental biotechnology calculations, CSV/Excel analysis, interactive plots,
standard-curve generation, experimental-design planning, and a manuscript checklist.

## Files
- `app.py` — main application
- `requirements.txt` — Python dependencies
- `.streamlit/config.toml` — theme/server configuration

## Run locally
```bash
python -m pip install -r requirements.txt
streamlit run app.py
```

## Deploy
Push these files to a GitHub repository, then deploy the repository on Streamlit Community Cloud.
Choose `app.py` as the entrypoint.

After deployment, the public app can be embedded into SciMantra/WordPress with:
```html
<iframe
  src="https://YOUR-APP.streamlit.app/?embed=true"
  style="height:1200px;width:100%;border:0;"
  loading="lazy">
</iframe>
```

Important: the app should be public if you want to embed it on a public website.
