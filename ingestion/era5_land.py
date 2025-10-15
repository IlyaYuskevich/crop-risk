import zipfile

import cdsapi
import fsspec
import xarray as xr

BUCKET = "nala-crop-risks"
ZARR = "era5-land/volumetric_soil_water_1_2024.zarr"
storage = {"anon": False, "client_kwargs": {"region_name": "eu-central-1"}}

dataset = "derived-era5-land-daily-statistics"
request = {
    "variable": [
        # "2m_temperature",
        "volumetric_soil_water_layer_1",
        # "volumetric_soil_water_layer_2",
        # "volumetric_soil_water_layer_3",
    ],
    "year": "2024",
    "month": ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"],
    "day": [
        "01", "02", "03",
        "04", "05", "06",
        "07", "08", "09",
        "10", "11", "12",
        "13", "14", "15",
        "16", "17", "18",
        "19", "20", "21",
        "22", "23", "24",
        "25", "26", "27",
        "28", "29", "30",
        "31"
    ],
    # "day": [
    #     "01",
    #     "03",
    #     "05",
    #     "07",
    #     "09",
    #     "11",
    #     "13",
    #     "15",
    #     "17",
    #     "19",
    #     "21",
    #     "23",
    #     "25",
    #     "27",
    #     "29",
    #     "31",
    # ],
    "daily_statistic": "daily_mean",
    "time_zone": "utc+00:00",
    "frequency": "1_hourly",
    "area": [72, -12, 32, 48],
}

c = cdsapi.Client()
res = c.retrieve(dataset, request)
url = res.location

local_path = res.download("/tmp/era5l")  # cdsapi will add the correct extension


# Create the Zarr store (append on 'time')
mapper = fsspec.get_mapper(f"s3://{BUCKET}/{ZARR}", s3=storage)


def _time_dim(ds):
    if "valid_time" in ds.dims:
        return "valid_time"
    if "time" in ds.dims:
        return "time"
    raise ValueError(f"No time dimension found; dims={list(ds.dims)}")


first = True
if zipfile.is_zipfile(local_path):
    with zipfile.ZipFile(local_path) as zf:
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
                tdim = _time_dim(ds)
                ds = ds.chunk({tdim: -1, "latitude": 50, "longitude": 50})
                if first:
                    ds.to_zarr(mapper, mode="w", zarr_format=2)
                    first = False
                else:
                    ds.to_zarr(mapper, mode="a", append_dim=tdim, zarr_format=2)
else:
    # Single NetCDF case (small requests may come back as .nc)
    print(f"Converting and uploading {local_path}")
    ds = xr.open_dataset(local_path, engine="h5netcdf", chunks="auto")
    try:
        ds = xr.decode_cf(ds)
    except Exception:
        pass
    tdim = _time_dim(ds)
    ds = ds.chunk({tdim: -1, "latitude": 50, "longitude": 50})
    ds.to_zarr(mapper, mode="w", zarr_format=2)

# consolidate metadata → O(1) opens (v2 only)
import zarr as z

z.consolidate_metadata(mapper)
print(f"s3://{BUCKET}/{ZARR}")
