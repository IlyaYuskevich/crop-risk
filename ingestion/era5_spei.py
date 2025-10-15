import io
import zipfile

import cdsapi
import fsspec
import requests
import xarray as xr

BUCKET = "nala-crop-risks"
ZARR = "era5-drought/spei_1-3-6_2023-2025.zarr"
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
    "year": [str(yr) for yr in range(2023, 2026)],
    "month": ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"],
    "area": [72, -12, 32, 48],  # Europe only; comment out for global
}

c = cdsapi.Client()
res = c.retrieve(dataset, request)
url = res.location

# Create the Zarr store (append on 'time')
mapper = fsspec.get_mapper(f"s3://{BUCKET}/{ZARR}", s3=storage)

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
            try:
                ds = xr.decode_cf(ds)
            except Exception:
                pass
            ds = ds.chunk({"time": -1, "lat": 50, "lon": 50})

            if first:
                ds.to_zarr(mapper, mode="w", zarr_format=2)
                first = False
            else:
                ds.to_zarr(mapper, mode="a", append_dim="time", zarr_format=2)

# consolidate metadata → O(1) opens (v2 only)
import zarr as z

z.consolidate_metadata(mapper)
print(f"s3://{BUCKET}/{ZARR}")
