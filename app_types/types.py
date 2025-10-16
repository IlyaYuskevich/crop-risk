import typing as t

CropSpecies = t.Literal["Wheat", "Bilberry"]
WeatherIndicator = t.Literal[
    "2m_temperature_min",
    "2m_temperature_max",
    "volumetric_soil_water_1",
    "volumetric_soil_water_2",
    "volumetric_soil_water_3",
    "leaf_area_index_low_vegetation",
    "spei_1-3-6_2023-2025"
]


class BandConfig(t.TypedDict):
    lo: str | int | float | None
    hi: str | int | float | None
    fill: str
    line: str | None


class CropStage(t.TypedDict):
    label: str
    start_month: int
    start_day: int
    color: str
    thresholds: dict[str, int | float]
    
class WeatherIndicatorsConfig(t.TypedDict):
    path: str
    var_name: str
    request_var: str
    request_aggregation: t.Literal["daily_mean", "daily_minimum", "daily_maximum"]


CropToStages = dict[CropSpecies, list[CropStage]]
PlotThresholdsConfig = dict[str, BandConfig]
IndicatorNameToConfig = dict[WeatherIndicator, WeatherIndicatorsConfig]
