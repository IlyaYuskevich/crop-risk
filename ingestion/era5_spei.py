import cdsapi, requests, fsspec, zipfile, io, xarray as xr, numpy as np

BUCKET = "nala-crop-risks"
ZARR   = "era5-drought/spei_1-3-6_2023-2025.zarr"
storage = {"anon": False, "client_kwargs": {"region_name": "eu-central-1"}}

dataset = "derived-drought-historical-monthly"
request = {
    "variable": ["standardised_precipitation_evapotranspiration_index"],
    "accumulation_period": [
        "1",
        # "3",
        # "6"
    ],
    "version": "1_0",
    "product_type": ["reanalysis"],
    "dataset_type": "intermediate_dataset",
    "year": ["2024", "2025"],
    "month": [
        "01", "02", "03",
        "04", "05", "06",
        "07", "08", "09",
        "10", "11", "12"
    ],
    "area": [72, -12, 32, 48] # Europe only; comment out for global
}

c = cdsapi.Client()
res = c.retrieve(dataset, request)
url = res.location

# Create the Zarr store (append on 'time')
mapper = fsspec.get_mapper(f"s3://{BUCKET}/{ZARR}", s3=storage)

def normalize(ds: xr.Dataset) -> xr.Dataset:
    """Ensure canonical dims (time, lat, lon) and a length-1 time dim."""
    # decode time if needed
    try:
        ds = xr.decode_cf(ds)
    except Exception:
        pass

    rename = {}
    if "latitude" in ds.dims:  rename["latitude"] = "lat"
    if "longitude" in ds.dims: rename["longitude"] = "lon"
    if "y" in ds.dims:         rename["y"] = "lat"
    if "x" in ds.dims:         rename["x"] = "lon"
    ds = ds.rename(rename)

    # time might be a coord but not a dim; make it a length-1 dim
    if "time" not in ds.dims:
        if "time" in ds.coords:
            ds = ds.expand_dims(time=[np.array(ds["time"].values).item()])  # make it a dim
        else:
            # fall back: try to synthesize a time coord from global attrs if present
            raise ValueError("No 'time' coordinate found in monthly file")

    # enforce chunking optimized for point time series
    # (all time in one chunk; small-ish spatial tiles)
    ds = ds.chunk({"time": -1, "lat": 50, "lon": 50})
    return ds

first = True
with requests.get(url, stream=True) as r:
    r.raise_for_status()
    zf = zipfile.ZipFile(io.BytesIO(r.content))

    for name in sorted(zf.namelist()):
        if not name.lower().endswith(".nc"):
            continue
        print(f"Converting and uploading {name}")
        with zf.open(name) as f:
            ds = xr.open_dataset(f, engine="h5netcdf", chunks="auto")
            ds = normalize(ds)

            if first:
                ds.to_zarr(mapper, mode="w", zarr_format=2)
                first = False
            else:
                ds.to_zarr(mapper, mode="a", append_dim="time", zarr_format=2)

# consolidate metadata → O(1) opens (v2 only)
import zarr as z
z.consolidate_metadata(mapper)
print(f"s3://{BUCKET}/{ZARR}")