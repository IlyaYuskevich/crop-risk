# Crops Climate Stress Dashboard

Interactive Streamlit app that monitors crop heat stress and drought risk across French departments and German districts using ERA5-Land daily aggregates. The dashboard highlights growing-stage thresholds, surfaces potential warning/alert periods, and lets users explore historical seasons with dynamic charts.

## Features
- Regional selector scoped to the centroids used in the Google Earth Engine export.
- Heat stress view with rolling 3-day maximum temperatures, growing-stage overlays, and automatic warning/alert call-outs.
- Drought view with 30-day rolling precipitation and stage-specific minimum precipitation thresholds.
- Built-in Streamlit navigation between heat and drought pages with synced query parameters for sharing filtered URLs.

## Requirements
- Python 3.13 (see `.python-version` for `pyenv` users)
- [PDM](https://pdm.fming.dev)

## Getting Started
```bash
# Clone the repository
$ git clone <repo-url>
$ cd crops

# (Optional) create and activate a virtual environment
$ pyenv install 3.13.0        # only if Python 3.13 is not yet available locally
$ pyenv local 3.13.0
$ python -m venv .venv
$ source .venv/bin/activate   # Windows: .venv\Scripts\activate

# Install dependencies with PDM (preferred)
$ pip install pdm
$ pdm install

```

### Data preparation
#### SPEI
Make sure that you authenticated in aws and have permissions to write to buckets on staging. Enter your API token and url from `https://xds-preprod.ecmwf.int/profile` to file ` ~/.cdsapirc.xds.preprod`.

`nvim ~/.cdsapirc.xds.preprod`

Export env variables `export CDSAPI_RC=~/.cdsapirc.xds.preprod`.

Then run `pdm run ./ingestion/era5_spei.py`.

#### ERA5-Land
Make sure that you authenticated in aws and have permissions to write to buckets on staging. Enter your API token and url from `https://cds.climate.copernicus.eu/profile` to file ` ~/.cdsapirc.cds.prod`.

`nvim ~/.cdsapirc.cds.prod`

Export env variables `export CDSAPI_RC=~/.cdsapirc.cds.prod`.

Then run `pdm run ./ingestion/era5_land.py`.

## Running the Streamlit app locally
```bash
$ streamlit run app.py
```

The app launches at `http://localhost:8501` by default. The sidebar exposes the region selector and crop-year dropdown; both pages share the same selection via URL query parameters, making it easy to bookmark or share a particular view.

## Deploying to Streamlit Cloud
1. Push the repository to GitHub or another Git provider.
2. In Streamlit Community Cloud, create a new app and point it to `app.py`.
3. Specify Python 3.13 in the app settings and add a `requirements.txt` generated with `pdm export --format requirements --output requirements.txt` (commit the file or upload it in the deployment UI).
4. Keep the default command `streamlit run app.py`. The included `.streamlit/config.toml` already configures a headless server on port 8501.
5. If you need scheduled data refreshes, automate `fetch_data.py` outside Streamlit (the Community Cloud environment cannot run Earth Engine exports interactively).

## Project layout
```
app.py                         # Global Streamlit configuration (shared styles/nav tweaks)
pages/Heat.py                  # Heat stress dashboard
pages/Drought.py               # Drought risk dashboard
constants/                     # Stage markers and agricultural calendar constants
data_transformations/heat.py   # Helper for heat-wave alert calculations
data/                          # ERA5 CSV exports and compiled Parquet data
parquet.py                     # CSV -> Parquet consolidation script
fetch_data.py                  # Google Earth Engine export pipeline
.streamlit/config.toml         # Streamlit server configuration
```

## Testing & linting
Developer dependencies include Ruff, Black, and Pytest. After installing the `dev` dependency group (`pdm install --group dev`), you can run:
```bash
$ pdm run ruff check
$ pdm run black .
$ pdm run pytest
```

