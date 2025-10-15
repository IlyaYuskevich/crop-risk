import typing as t

CropSpecies = t.Literal["Wheat", "Bilberry"]

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
    
CropToStages = dict[CropSpecies, list[CropStage]]
PlotThresholdsConfig = dict[str, BandConfig]