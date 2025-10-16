from app_types.types import IndicatorNameToConfig

INDICATOR_NAME_TO_CONFIG: IndicatorNameToConfig = {
    "2m_temperature_max": {
        "path": "era5-land/",
        "var_name": "t2m",
        "request_aggregation": "daily_maximum",
        "request_var": "2m_temperature",
    },
    "2m_temperature_min": {
        "path": "era5-land/",
        "var_name": "t2m",
        "request_aggregation": "daily_minimum",
        "request_var": "2m_temperature",
    },
    "volumetric_soil_water_1": {
        "path": "era5-land/",
        "var_name": "swvl1",
        "request_aggregation": "daily_mean",
        "request_var": "volumetric_soil_water_layer_1",
    },
    "volumetric_soil_water_2": {
        "path": "era5-land/",
        "var_name": "swvl2",
        "request_aggregation": "daily_mean",
        "request_var": "volumetric_soil_water_layer_2",
    },
    "volumetric_soil_water_3": {
        "path": "era5-land/",
        "var_name": "swvl3",
        "request_aggregation": "daily_mean",
        "request_var": "volumetric_soil_water_layer_3",
    },
    "leaf_area_index_low_vegetation": {
        "path": "era5-land/",
        "var_name": "lai_lv",
        "request_aggregation": "daily_mean",
        "request_var": "leaf_area_index_low_vegetation",
    },
    "spei_1-3-6_2023-2025": {
        "path": "era5-drought/",
        "var_name": "SPEI1",
        "request_aggregation": "daily_mean",
        "request_var": "standardised_precipitation_evapotranspiration_index",
    }
}