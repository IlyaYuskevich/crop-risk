import typing as t

from app_types.types import CropSpecies

CROP_SPECIES: tuple[CropSpecies] = t.get_args(CropSpecies)

class Season(t.TypedDict):
    start_month: int
    start_day: int
    end_month: int
    end_day: int
    
SEASON_BOUNDARIES: dict[CropSpecies, Season] = {
    "Wheat": {
        "start_month": 9,
        "start_day": 1,
        "end_month": 8,
        "end_day": 31,
    },
    "Bilberry": {
        "start_month": 11,
        "start_day": 1,
        "end_month": 10,
        "end_day": 31,
    }
}